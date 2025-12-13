import os
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.core.node_parser import TokenTextSplitter

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

splitter = TokenTextSplitter(
    chunk_size=100,
    chunk_overlap=10,
    separator="\n"
)

reader = SimpleDirectoryReader(input_dir="./doc")
documents = reader.load_data()


def main():

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