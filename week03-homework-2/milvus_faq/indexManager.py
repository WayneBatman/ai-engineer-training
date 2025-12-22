import asyncio
import os.path

import pandas as pd
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.vector_stores.milvus import MilvusVectorStore
from paddleocr import DocUnderstanding
from sqlalchemy import false

import config

# 使用单例模式确保全局只有一个 IndexManager 实例
_query_engine = None
_index = None

async def _init_index():
    global _query_engine, _index

    print("开始初始化向量数据库Milvus并创建索引")
    vectorstore = MilvusVectorStore(
        uri = config.MILVUS_URI,
        collection_name = config.MILVUS_COLLECTION_NAME,
        dim=config.MILVUS_DIMENSION,
        overwrite=False,  # 设置为 False 以便重用现有集合
    )

    print("创建存储上下文")
    storage_context = StorageContext.from_defaults(vector_store=vectorstore)

    if not os.path.exists(config.FAQ_FILE):
        print(f"数据文件{config.FAQ_FILE}不存在。创建一个空索引")
        _index = VectorStoreIndex.from_documents(
            document=[],
            storage_context=storage_context
        )
    else:
        try:
            _index = VectorStoreIndex.from_vector_store(
                vector_store=vectorstore,
            )
            print("从现有的Milvus数据库中加载索引")
        except Exception:
            print("无法从现有集合加载，将从文件构建索引。")
            _index = await  _build_index_from_file(storage_context)

    _query_engine = _index.as_query_engine(similarity_top_k = config.SIMILAR_TOP_K)
    print("完成初始化向量数据库Milvus并创建索引")

async def _build_index_from_file(storage_context : StorageContext) -> VectorStoreIndex:
    print(f"从文件{config.FAQ_FILE}构建索引")
    df = pd.read_csv(config.FAQ_FILE)
    documents = []

    for _, row in df.iterrows():
        doc_text = f"问题: {row['question']}\n答案: {row['answer']}"
        documents.append(Document(text=doc_text,metadata={"question": row['question'],"path": config.FAQ_FILE}))

    splitter = SemanticSplitterNodeParser.from_defaults(
        embed_model=config.EMBED_MODEL,
    )

    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        transformations=[splitter]
    )

    return index

async def get_query_engine():
    if _query_engine is None:
        await _init_index()
    return _query_engine

async def update_index():
    global _query_engine, _index

    print("开始热更新索引")

    # 创建一个新的 Milvus 存储，并设置 overwrite=True 来清空旧集合
    vectorstore = MilvusVectorStore(
        uri=config.MILVUS_URI,
        collection_name=config.MILVUS_COLLECTION_NAME,
        dim=config.MILVUS_DIMENSION,
        overwrite=True,
    )
    storage_context = StorageContext.from_defaults(vector_store=vectorstore)

    # 从文件重新构建索引
    _index = await _build_index_from_file(storage_context)
    _query_engine = _index.as_query_engine(similarity_top_k=config.SIMILAR_TOP_K)

    print("索引热更新完成。")
    return {"message": "索引已成功更新。"}

# 模块加载的时候，就初始化
_init_index()

