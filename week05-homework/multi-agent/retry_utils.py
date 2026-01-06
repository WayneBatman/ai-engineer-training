import asyncio
from functools import wraps
from typing import Callable, Any, Optional
import datetime


class RetryStrategy:
    """重试策略管理器"""

    def __init__(self):
        self.retry_logs = []

    async def execute_with_retry(
        self,
        node_name: str,
        node_func: Callable,
        state: dict,
        backup_func: Optional[Callable] = None,
        max_same_agent_retries: int = 2
    ):
        """
        执行带重试的节点函数

        参数:
            node_name: 节点名称
            node_func: 主节点函数
            state: 当前状态
            backup_func: 备用节点函数（二级重试用）
            max_same_agent_retries: 同一代理的最大重试次数
        """
        retry_count = state.get('retry_count', 0)
        error_log = state.get('error_log', [])

        # 重试循环
        while retry_count < max_same_agent_retries + 1:  # +1 包含初始尝试
            try:
                print(f"[重试策略] {node_name} - 尝试 {retry_count + 1}/{max_same_agent_retries + 1}")
                result = await node_func(state)

                # 成功执行，记录并返回结果
                if retry_count > 0:
                    success_msg = f"[重试成功] {node_name} 在第 {retry_count + 1} 次尝试后成功"
                    error_log.append(success_msg)
                    print(success_msg)

                # 重置重试计数
                result['retry_count'] = 0
                result['error_log'] = error_log

                return result

            except Exception as e:
                retry_count += 1
                error_msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {node_name} 执行失败 (尝试 {retry_count}/{max_same_agent_retries + 1}): {str(e)}"
                error_log.append(error_msg)
                print(error_msg)

                # 如果达到相同代理的最大重试次数，尝试备用代理
                if retry_count >= max_same_agent_retries and backup_func:
                    print(f"[重试策略] {node_name} - 切换至备用代理")
                    try:
                        # 切换到备用代理
                        result = await backup_func(state)
                        backup_msg = f"[重试成功] {node_name} 备用代理执行成功"
                        error_log.append(backup_msg)
                        print(backup_msg)

                        # 重置重试计数
                        result['retry_count'] = 0
                        result['error_log'] = error_log
                        return result
                    except Exception as backup_error:
                        backup_error_msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {node_name} 备用代理执行失败: {str(backup_error)}"
                        error_log.append(backup_error_msg)
                        print(backup_error_msg)
                        # 继续三级重试

                # 如果所有重试都失败，进入三级重试
                if retry_count >= max_same_agent_retries + 1:
                    print(f"[重试策略] {node_name} - 所有重试均失败")
                    break

        # 所有重试都失败，返回错误信息
        final_error = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {node_name} 在经过 {retry_count} 次尝试后仍未成功"
        error_log.append(final_error)

        # 询问用户补充信息（三级重试）
        print(f"\n{'='*50}")
        print(f"⚠️  {node_name} 执行失败")
        print(f"错误信息: {e}")
        print(f"{'='*50}\n")

        return {
            'retry_count': 0,
            'error_log': error_log,
            'error': str(e),
            'failed_node': node_name
        }


def with_retry(max_same_agent_retries: int = 2):
    """
    装饰器：为节点函数添加重试能力

    参数:
        max_same_agent_retries: 同一代理的最大重试次数
    """
    def decorator(node_func):
        @wraps(node_func)
        async def wrapper(self, state):
            retry_strategy = RetryStrategy()
            node_name = node_func.__name__.replace('_node', '')

            # 定义备用代理函数（如果存在）
            backup_func = None
            backup_name = f"{node_name}_backup"
            if hasattr(self, f"{backup_func.__name__}_backup"):
                backup_func = getattr(self, f"{node_func.__name__}_backup")

            result = await retry_strategy.execute_with_retry(
                node_name=node_name,
                node_func=lambda s: node_func(self, s),
                state=state,
                backup_func=backup_func,
                max_same_agent_retries=max_same_agent_retries
            )

            return result

        return wrapper
    return decorator
