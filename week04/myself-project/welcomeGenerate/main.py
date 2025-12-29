import uvicorn
from fastapi import FastAPI

from fastAPI import router

app = FastAPI(
    title="欢迎语生成器",
    description="这是我的一个欢迎语生成器",
    version="1.0.0"
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "通过访问 /docs 查看 API 文档."
    }

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    main()