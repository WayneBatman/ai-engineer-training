#一些全局设置
import os

from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.llms.dashscope import DashScope
from llama_index.llms.openai_like import OpenAILike

print("++++开始初始化++++++")

# 加载.env文件
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

print(f"NEO4J_URI:{NEO4J_URI}")
print(f"NEO4J_USERNAME:{NEO4J_USERNAME}")
print(f"NEO4J_PASSWORD:{NEO4J_PASSWORD}")
print(f"NEO4J_DATABASE:{NEO4J_DATABASE}")

# --- 数据和索引路径配置 ---
DATA_DIR = "data"
INDEX_DIR = "vectorIndex"

SIMILAR_TOP_K = 2

#阿里千问的api_key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

# Settings.llm = OpenAILike(
#     model="qwen-plus",
#     api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     api_key=DASHSCOPE_API_KEY,
#     is_chat_model=True
# )

Settings.llm = DashScope(model_name="qwen-plus", api_key=DASHSCOPE_API_KEY,enable_search=False)

Settings.embed_model = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
    embed_batch_size=6,
    embed_input_length=8192
)



print("++++结束初始化++++++")