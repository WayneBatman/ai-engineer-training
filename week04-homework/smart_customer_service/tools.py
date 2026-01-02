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

@tool
def query_order(order_id) -> dict:
    """
        工具：根据订单号查询订单信息）。

    参数：
        order_id: 订单号

    返回：
        返回订单时间以及状态
    """
    print(f"--- [工具调用] 正在查询订单号: {order_id} ---")
    mock_db = {
        "SN202500001": {"status": "已发货", "tracking_number": "SF202601030089", "items": ["鱼书-深度学习入门-基于Python....."]},
        "SN202500002": {"status": "已发货", "tracking_number": "ZT202601040078", "items": ["鱼书-深度学习进阶-自然语言....."]},
        "SN202500003": {"status": "待支付", "tracking_number": None, "items": ["鱼书-生成模型进阶"]},
        "SN202500004": {"status": "已完成", "tracking_number": "YT202601040001", "items": ["极客时间台历"]},
    }
    order_info = mock_db.get(order_id)
    if order_info:
        return {
            "success": True,
            "order_id": order_id,
            "status": order_info["status"],
            "tracking_number": order_info["tracking_number"],
            "details": f"订单中的商品: {', '.join(order_info['items'])}"
        }
    else:
        return {
            "success": False,
            "order_id": order_id,
            "error": "未找到该订单，请检查订单号是否正确。"
        }

@tool
def apply_refund(order_id: str, reason: str) -> dict:
    """
    为指定订单号的订单申请退款。
    需要提供订单号和退款原因。
    """
    print(f"--- [工具调用] 正在为订单号 {order_id} 申请退款，原因: {reason} ---")
    if "SN" in order_id:
        refund_id = f"REFUND_{order_id}"
        return {
            "success": True,
            "order_id": order_id,
            "refund_id": refund_id,
            "message": "退款申请已提交，审核通过后将原路退回。"
        }
    else:
        return {
            "success": False,
            "order_id": order_id,
            "error": "无效的订单号，无法申请退款。"
        }
