import os
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, PromptTemplate
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.core.node_parser import TokenTextSplitter, SentenceSplitter, SentenceWindowNodeParser

EVAL_TEMPLATE_STR = (
    "我们提供了一个标准答案和一个由模型生成的回答。请你判断模型生成的回答在语义上是否与标准答案一致、准确且完整。\n"
    "请只回答 '是' 或 '否'。\n"
    "\n"
    "标准答案：\n"
    "----------\n"
    "{ground_truth}\n"
    "----------\n"
    "\n"
    "模型生成的回答：\n"
    "----------\n"
    "{generated_answer}\n"
    "----------\n"
)
eval_template = PromptTemplate(template=EVAL_TEMPLATE_STR)

def evaluate_splitter(splitter, documents, question, ground_truth, splitter_name):
    """
    评估不同的分割器对检索和生成质量的影响。

    Args:
        splitter: 用于切分文档的 LlamaIndex 分割器对象。
        documents: 待处理的文档列表。
        question: 用于查询的问题字符串。
        ground_truth: 问题的标准答案。
        splitter_name: 分割器的名称，用于在结果中标识。
    """
    print(f"--- 开始评估: {splitter_name} ---")

    # 1. 使用指定的分割器切分文档
    nodes = splitter.get_nodes_from_documents(documents)

    # 2. 建立索引
    index = VectorStoreIndex(nodes)

    # 3. 创建查询引擎
    # 特别处理 SentenceWindowNodeParser，因为它需要一个后处理器
    if isinstance(splitter, SentenceWindowNodeParser):
        # 注意：句子窗口切片需要特殊的后处理器
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            node_postprocessors=[MetadataReplacementPostProcessor(target_metadata_key="window")]
        )
    else:
        query_engine = index.as_query_engine(similarity_top_k=5)

    # 4. 检索上下文
    retrieved_nodes = query_engine.retrieve(question)
    retrieved_context = "\n\n".join([node.get_content() for node in retrieved_nodes])

    # 5. 评估：检索到的上下文是否包含答案
    # 使用标准答案的前15个字符作为关键信息进行检查
    context_contains_answer = "是" if ground_truth[:15] in retrieved_context else "否"

    # 6. 评估：LLM 生成的回答是否准确完整
    response = query_engine.query(question)
    generated_answer = str(response)
    # 使用 LLM 作为评判者来评估答案的准确性
    eval_response = Settings.llm.predict(
        eval_template,
        ground_truth=ground_truth,
        generated_answer=generated_answer
    )
    answer_is_accurate = "是" if "是" in eval_response else "否"

    # 7. 评估：上下文冗余程度（人工评分）
    print("\n检索到的上下文：")
    print(retrieved_context)
    redundancy_score = input(f"请为【{splitter_name}】的上下文冗余程度打分 (1-5, 1表示最不冗余, 5表示最冗余): ")
    while redundancy_score not in ['1', '2', '3', '4', '5']:
        redundancy_score = input("无效输入。请输入1到5之间的整数: ")

    # 8. 存储结果
    # 使用函数属性来跨多次调用存储结果
    if not hasattr(evaluate_splitter, "results"):
        evaluate_splitter.results = []

    evaluate_splitter.results.append({
        "分割器": splitter_name,
        "上下文包含答案": context_contains_answer,
        "回答准确": answer_is_accurate,
        "上下文冗余度(1-5)": int(redundancy_score),
        "生成回答": generated_answer.strip().replace("\n", " ")[:100] + "..."
    })

    print(f"--- 完成评估: {splitter_name} ---\n")


def main():
    Settings.llm = OpenAILike(
        model="qwen-plus",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        is_chat_model=True
    )

    Settings.embed_model = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
        embed_batch_size=6,
        embed_input_length=8192
    )

    # 句子切片
    splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50
    )

    # 定义具体的问题和标准答案，这里以量子计算为例
    question = "a80C51的时钟源是多少？"
    ground_truth = "a80C51的时钟源：内部高精度 RC 振荡器（±1% 精度）、外部晶振（4~24MHz）、外部时钟输入。"

    # splitter = TokenTextSplitter(
    #     chunk_size=100,
    #     chunk_overlap=10,
    #     separator="\n"
    # )

    reader = SimpleDirectoryReader(input_dir="./doc")
    documents = reader.load_data()

    evaluate_splitter(splitter, documents, question, ground_truth, "Sentence")

    nodes = splitter.get_nodes_from_documents(documents)

    for node in nodes:
        print(node.text)
        print(node.metadata)

    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    inputStr = input("请输入你想检索的内容：\n")
    response = query_engine.query(inputStr)
    print(response)

if __name__ == "__main__":
    main()