import uvicorn
from fastapi import FastAPI
from interfaceApi import router as api_router

app = FastAPI(
    title="GraphRAG 多跳问答系统",
    description="一个融合了文档检索 (RAG) 和知识图谱 (KG) 的高级问答 API",
    version="1.0.0",
)


app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用 GraphRAG API. "
                   "请先运行 'python -m graph_rag.graph_builder' 来构建知识图谱, "
                   "然后访问 /docs 查看 API 文档."
    }

def main():
# 作业的入口写在这里。你可以就写这个文件，或者扩展多个文件，但是执行入口留在这里。
# 在根目录可以通过python -m graph_rag.main 运行
    print("启动 FastAPI 服务...")
    print("在启动服务前，请运行了图谱构建脚本:")
    print("python ./buildGraph.py")

    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()