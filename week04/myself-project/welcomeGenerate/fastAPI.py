import uvicorn
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from ChainChat import ChatChain

router = APIRouter()

chat_chain = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    session_id: str

@router.on_event("startup")
async def startup_event():
    global chat_chain
    print("系统启动时执行")
    chat_chain = ChatChain()
    await chat_chain.initialize()

@router.on_event("shutdown")
async def shutdown_event():
    print("系统结束时执行")

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "langchain_version": "0.3.x"}

@router.post("/hello",response_model=ChatResponse)
async def hello(request: ChatRequest):
    result = await chat_chain.generate_prompt(name = request.message)
    return {
        "reply":result,
        "session_id":request.session_id
    }

