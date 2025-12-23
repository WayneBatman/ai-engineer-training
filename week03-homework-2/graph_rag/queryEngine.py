import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core.query_engine import KnowledgeGraphQueryEngine
from llama_index.core.prompts import PromptTemplate, PromptType

import config

# --- 全局变量 ---
_rag_query_engine = None
_kg_query_engine = None

def _initGraphIndex():
    global _rag_query_engine

    if not os.path.exists(config.INDEX_DIR):
        print("未找到向量索引")
        documents = SimpleDirectoryReader(
            input_files=[os.path.join(config.DATA_DIR, "company.txt")]
        ).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir = config.INDEX_DIR)
        print(f"向量索引已创建")
    else:
        print(f"从 '{config.INDEX_DIR}' 加载现有向量索引...")
        storage_context = StorageContext.from_defaults(persist_dir=config.INDEX_DIR)
        index = load_index_from_storage(storage_context)
        print("向量索引加载成功。")

    _rag_query_engine = index.as_query_engine(similarity_top_k = config.SIMILAR_TOP_K)

def _initKgQueryEngine():
    global _kg_query_engine

    graph_store = Neo4jGraphStore(
        username=config.NEO4J_USERNAME,
        password=config.NEO4J_PASSWORD,
        url=config.NEO4J_URI,
        database=config.NEO4J_DATABASE,
    )

    #https://github.com/run-llama/llama_index/issues/16847
    DEFAULT_GRAPH_QUERY_PROMPT = PromptTemplate(
        """
        根据问题产生查询图谱
        {query_str}
        """,
        prompt_type=PromptType.TEXT_TO_GRAPH_QUERY,
    )

    # 这个查询引擎能将自然语言转换为 Cypher 查询
    _kg_query_engine = KnowledgeGraphQueryEngine(
        storage_context = StorageContext.from_defaults(graph_store=graph_store),
        llm=config.Settings.llm,
        graph_query_synthesis_prompt=DEFAULT_GRAPH_QUERY_PROMPT,
        verbose=True, # 打印生成的 Cypher 查询，便于调试
    )
    print("知识图谱初始化成功。")

def multiHopQuery(question: str):
    if not _rag_query_engine or not _kg_query_engine:
        raise RuntimeError("请等待查询引擎初始化完成")

    reasoning_path = []
    # 1. RAG 检索：识别问题中的核心实体
    entity_extraction_prompt = PromptTemplate(
        "从以下问题中提取出公司或机构的名称：'{question}'\n"
        "只返回名称，不要添加任何其他文字。"
    )
    formatted_prompt = entity_extraction_prompt.format(question=question)
    entity_name_response = config.Settings.llm.complete(formatted_prompt)
    entity_name = entity_name_response.text.strip()
    print(f"步骤 1: 从问题 '{question}' 中识别出核心实体 -> '{entity_name}'")
    reasoning_path.append(f"步骤 1: 从问题 '{question}' 中识别出核心实体 -> '{entity_name}'")

    cypher_query = ""
    if "最大股东" in question or "控股" in question:
        cypher_query = f"""
        MATCH (shareholder:Entity)-[r:HOLDS_SHARES_IN]->(company:Entity {{name: '{entity_name}'}})
        RETURN shareholder.name AS shareholder, r.share_percentage AS percentage
        ORDER BY percentage DESC
        LIMIT 1
        """
        reasoning_path.append(f"步骤 2: 识别到关键词'最大股东'，构造精确 Cypher 查询在图谱中查找。")
        reasoning_path.append(f"   - Cypher 查询: {cypher_query.strip()}")

        # "detail": "处理查询时发生内部错误: 'KnowledgeGraphQueryEngine' object has no attribute 'storage_context'"
        #这里一直在报错，但是我看KnowledgeGraphQueryEngine中，有这个属性才对
        # graph_store = _kg_query_engine.storage_context.graph_store
        graph_store = _kg_query_engine.__getattribute__("graph_store")
        graph_response = graph_store.query(cypher_query)
        kg_result_text = str(graph_response)

    else:
        print(f"步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。")
        reasoning_path.append(f"步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。")

        kg_response = _kg_query_engine.query(f"查询与 '{entity_name}' 相关的信息")
        kg_result_text = kg_response.response

        if 'cypher_query' in kg_response.metadata:
            reasoning_path.append(f"   - 生成的 Cypher 查询: {kg_response.metadata['cypher_query'].strip()}")

    reasoning_path.append(f"   - 图谱查询结果: {kg_result_text}")

    # 3. RAG 补充信息
    rag_response = _rag_query_engine.query(f"提供关于 '{entity_name}' 的详细信息。")
    rag_context = "\n\n".join([node.get_content() for node in rag_response.source_nodes])
    reasoning_path.append(f"步骤 3: 通过 RAG 检索关于 '{entity_name}' 的背景文档信息。")
    reasoning_path.append(f"   - RAG 检索到的上下文: {rag_context[:200]}...")  # 仅显示部分

    # 4. LLM 生成最终回答
    final_answer_prompt = PromptTemplate(
        "你是一个专业的金融分析师。请根据以下信息，以清晰、简洁的语言回答用户的问题。\n"
        "--- 用户问题 ---\n{question}\n\n"
        "--- 知识图谱查询结果 ---\n{kg_result}\n\n"
        "--- 相关文档信息 ---\n{rag_context}\n\n"
        "--- 最终回答 ---\n"
    )

    formatted_prompt = final_answer_prompt.format(
        question=question,
        kg_result=kg_result_text,
        rag_context=rag_context
    )

    reasoning_path.append("步骤 4: 综合图谱结果和文档信息，由 LLM 生成最终的自然语言回答。")
    final_response = config.Settings.llm.complete(formatted_prompt)
    final_answer = final_response.text

    return {
        "final_answer": final_answer,
        "reasoning_path": reasoning_path
    }

# --- 初始化所有引擎 ---
def initializeAll():
    _initGraphIndex()
    _initKgQueryEngine()


# 在模块加载时执行初始化
initializeAll()