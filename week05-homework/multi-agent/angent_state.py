from typing import TypedDict, List, Any, Optional


class AgentState(TypedDict):
    """定义图的状态"""
    topic: str
    style: str
    length: int
    research_report: str
    draft: str
    review_suggestions: str
    final_article: str
    log: List[str]
    mcp_client: Any
    # 重试相关状态
    retry_count: Optional[int]  # 当前节点的重试次数
    error_log: List[str]  # 错误和重试日志
