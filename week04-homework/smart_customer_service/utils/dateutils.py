from datetime import datetime


def get_current_time() -> str:
    """获取当前时间，并且按xxxx-xx-xx xx:xx:xx格式返回"""
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    #print("格式化后的时间：", formatted_time)
    return formatted_time