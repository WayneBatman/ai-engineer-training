#一些全局设置
import os

from dotenv import load_dotenv

print("++++开始初始化++++++")

# 加载.env文件
load_dotenv()

#阿里千问的api_key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME")

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"


print("++++结束初始化++++++")