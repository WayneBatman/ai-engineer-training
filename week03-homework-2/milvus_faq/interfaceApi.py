from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status

import indexManager

router = APIRouter()

class QueryRequest(BaseModel):
    question : str

class QueryResponse(BaseModel):
    question : str
    answer : str
    score : float

@router.post("/query",response_model=list[QueryResponse])
async def query_faq(request: QueryRequest):
    if not request.question:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="请问我有什么可以帮助您？")

    print(f"当前用户问题: {request.question}")
    query_engine = await indexManager.get_query_engine()
    response = query_engine.query(request.question)

    if not response.source_nodes:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="我还要继续学习，暂时无法回复您")

    results = []

    for node in response.source_nodes:
        # 从节点文本中解析出原始问题和答案
        textparts = node.get_text().split('\n答案: ')
        original_question = textparts[0].replace('问题: ', '')
        answer = textparts[1] if len(textparts) > 1 else "我还要继续学习，暂时无法回复您"

        results.append(
            QueryResponse(
                question=original_question,
                answer=answer,
                score=node.get_score() or 0.0
            )
        )

    return results

@router.post("/update-index")
async def update_faq_index():
    """
    触发知识库的热更新。
    系统将从 data/faq.csv 重新加载并建立索引。
    """
    try:
        result = await indexManager.update_index()
        return {"status": "success", "message": result["message"]}
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"索引更新失败: {str(e)}")