#一些全局设置
import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.llms.openai_like import OpenAILike

print("++++开始初始化++++++")

# 加载.env文件
load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT")
MILVUS_URI = os.getenv("MILVUS_URI")
MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME")
MILVUS_DIMENSION = os.getenv("MILVUS_DIMENSION")
MILVUS_INDEX_DIR = os.getenv("MILVUS_INDEX_DIR")

print(f"MILVUS_HOST:{MILVUS_HOST}")
print(f"MILVUS_PORT:{MILVUS_PORT}")
print(f"MILVUS_URI:{MILVUS_URI}")
print(f"MILVUS_COLLECTION_NAME:{MILVUS_COLLECTION_NAME}")
print(f"MILVUS_DIMENSION:{MILVUS_DIMENSION}")
print(f"MILVUS_DIMENSION:{MILVUS_INDEX_DIR}")

# --- 数据和索引路径配置 ---
DATA_DIR = "data"
FAQ_FILE = os.path.join(DATA_DIR, "faq.csv")

SIMILAR_TOP_K = 2


#阿里千问的api_key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

Settings.llm = OpenAILike(
    model="qwen-plus",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=DASHSCOPE_API_KEY,
    is_chat_model=True
)

Settings.embed_model = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
    embed_batch_size=6,
    embed_input_length=8192
)

# 使用通义千问的文本嵌入模型
EMBED_MODEL = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
    api_key=DASHSCOPE_API_KEY
)


print("++++结束初始化++++++")