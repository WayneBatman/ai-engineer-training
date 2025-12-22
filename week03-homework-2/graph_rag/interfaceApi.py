from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette import status

import queryEngine

router = APIRouter()

class QueryRequest(BaseModel):
    question : str = Field(..., example="上汽通用五菱的最大股东是谁？")

class QueryResponse(BaseModel):
    question : str
    answer : str
    score : float

@router.post("/query",response_model=list[QueryResponse])
async def query_faq(request: QueryRequest):
    if not request.question:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="请问我有什么可以帮助您？")

    print(f"当前用户问题: {request.question}")

    try:
        result = queryEngine.multiHopQuery(request.question)
        return result
    except Exception as e:
        # 打印详细错误信息到服务器日志，方便调试
        print(f"查询处理时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"处理查询时发生内部错误: {str(e)}")
