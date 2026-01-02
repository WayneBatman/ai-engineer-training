from langchain.tools import tool
from dateutils import *

@tool
def get_date_from_question(question :str ) -> str:
    """
    工具：从用户问题中解析出对应的日期（支持“昨天”“今天”“明天”等表述）。

    参数：
        question: 用户包含时间表述的问题（如“昨天的订单”“后天的会议”）

    返回：
        解析后的日期字符串（格式如YYYY-MM-DD）；若无法解析则返回提示信息。
    """
    print(f"--- [工具调用] 正在解析时间段: {question} ---")

    if "昨天" in question:
        target_date = get_yesterday()
    elif "前天" in question:
        target_date = get_day_before_yesterday()
    elif "今天" in question:
        target_date = get_today()
    elif "明天" in question:
        target_date = get_tomorrow()
    elif "后天" in question:
        target_date = get_day_after_tomorrow()
    else:
        return "无法解析该时间，我还需要多学习。"

    return target_date