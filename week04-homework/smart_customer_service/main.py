import uvicorn
from fastapi import FastAPI
from interfaceapi import router as api_router

app = FastAPI(
    title="智能客服系统",
    description="这个一个简单的智能客服系统",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用 智能客服 API. "
                   "然后访问 /docs 查看 API 文档."
    }


def main():
# 作业的入口写在这里。你可以就写这个文件，或者扩展多个文件，但是执行入口留在这里。
# 在根目录可以通过python -m base_chat_system.main 运行
    print("启动 FastAPI 服务...")

    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()