from datetime import datetime, timedelta

DAY_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

current_time = datetime.now()
current_day = current_time.today()

def get_current_time() -> str:
    """获取当前时间，并且按xxxx-xx-xx xx:xx:xx格式返回"""
    formatted_time = current_time.strftime(TIME_FORMAT)
    #print("格式化后的时间：", formatted_time)
    return formatted_time

def get_today() -> str:
    """获取今天"""
    today = current_day.strftime(DAY_FORMAT)
    return today

def get_yesterday() -> str:
    """获取昨天"""
    yesterday = (current_day - timedelta(days=1)).strftime(DAY_FORMAT)
    return yesterday

def get_tomorrow() -> str:
    """获取明天"""
    tomorrow = (current_day + timedelta(days=1)).strftime(DAY_FORMAT)
    return tomorrow

def get_day_before_yesterday() -> str:
    """获取前天"""
    day_before_yesterday = (current_day - timedelta(days=2)).strftime(DAY_FORMAT)
    return day_before_yesterday

def get_day_after_tomorrow() -> str:
    """获取后天"""
    day_after_tomorrow = (current_day + timedelta(days=2)).strftime(DAY_FORMAT)
    return day_after_tomorrow