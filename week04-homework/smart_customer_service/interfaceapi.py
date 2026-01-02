from typing import Optional
from starlette import status

import dateutils
from agentservice import service_manager
from graphservice import GraphManager

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

graph_manager = GraphManager(service_manager)

class HotUpdateRequest(BaseModel):
    modelname: str # e.g., "qwen-max" or "default"

class ChatRequest(BaseModel):
    userid: str
    question : str

#不能混合继承
#class ChatResponse(BaseModel, Exception):
class ChatResponse(BaseModel):
    httpstatus: int  # HTTP状态码（如200/400/500）
    message: str     # 服务信息提示（如"服务正常"/"服务异常"）
    data: Optional[dict] = None  # 业务数据（包含time和info）

# 单独定义自定义异常类（继承Exception）
class ServiceError(Exception):
    def __init__(self, httpstatus: int, message: str):
        self.httpstatus = httpstatus
        self.message = message

@router.get("/health", response_model=ChatResponse)
def health_check():
        try:
            data = {
                "time": dateutils.get_current_time(),
                "serviceInfo": service_manager.get_services_status()
            }
            return ChatResponse(
                httpstatus=status.HTTP_200_OK,
                message="当前服务健康",
                data=data
            )
        except Exception as e:
            print(f"当前服务异常，异常信息：{e}")
            raise ServiceError(
                httpstatus=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message = f"当前服务不健康，原因{e}"
            )

@router.post("/chatAgent", response_model=ChatResponse)
def chatAgent(request: ChatRequest):
    if not request.question:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="请问我有什么可以帮助您？")

    print(f"当前用户问题: {request.question}")

    try:
        reply = service_manager.chat_response(request.question)
        return ChatResponse(
            httpstatus=status.HTTP_200_OK,
            message="请求成功",
            data={
                "reply": reply
            }
        )
    except Exception as e:
        print(f"当前服务异常，异常信息：{e}")
        raise ServiceError(
            httpstatus=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"当前服务报错，原因{e}"
        )

@router.post("/chatGraph", response_model=ChatResponse)
def chatGraph(request: ChatRequest):
    if not request.question:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="请问我有什么可以帮助您？")

    print(f"当前用户问题: {request.question}")

    try:
        reply = graph_manager.chat_response(request.question,request.userid)
        return ChatResponse(
            httpstatus=status.HTTP_200_OK,
            message="请求成功",
            data={
                "reply": reply
            }
        )
    except Exception as e:
        print(f"当前服务异常，异常信息：{e}")
        raise ServiceError(
            httpstatus=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"当前服务报错，原因{e}"
        )

@router.post("/hot-update", summary="热更新模型或工具")
async def hot_update(request: HotUpdateRequest):
    try:
        service_manager.update_llm(request.modelname)

        # 更新后，重新加载图
        graph_manager.reload_graph()

        return {"status": "success", "message": "热更新完成.","data": service_manager.get_services_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"热更新失败: {e}")