from smart_customer_service.utils.dateutils import get_current_time

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    question : str

class QueryResponse(BaseModel):
    answer: str

@router.get("/health", response_model=QueryResponse)
def health_check():
    return QueryResponse(answer=f"status ok,server time is {get_current_time()}")