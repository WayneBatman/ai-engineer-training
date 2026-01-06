from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage

import angent_state as AgentState
from retry_utils import RetryStrategy


class ArticleAgentNode:
    def __init__(self, mcp_tools: list):
        self.mcp_tools = {tool.name: tool for tool in mcp_tools}
        self.llm = ChatTongyi(model="qwen-max")
        self.retry_strategy = RetryStrategy()
        # 测试模式：用于测试重试机制
        self.test_mode = False
        self.test_fail_count = {}

    async def call_mcp_tool(self, tool_name: str, **kwargs):
        tool = self.mcp_tools[tool_name]
        result = await tool.ainvoke(kwargs)
        # 处理返回结果，确保是字符串
        if isinstance(result, list):
            if len(result) == 1:
                item = result[0]
                if isinstance(item, dict) and 'text' in item:
                    return item['text']
                elif isinstance(item, str):
                    return item
                elif hasattr(item, 'text'):
                    return item.text
                elif hasattr(item, 'content'):
                    return item.content
            # 如果是多个项目，尝试提取所有文本
            texts = []
            for item in result:
                if isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                elif isinstance(item, str):
                    texts.append(item)
                elif hasattr(item, 'text'):
                    texts.append(item.text)
                elif hasattr(item, 'content'):
                    texts.append(item.content)
            return '\n'.join(texts) if texts else str(result)
        elif isinstance(result, dict):
            if 'text' in result:
                return result['text']
        if hasattr(result, 'content'):
            return result.content
        return str(result)

    async def research_node_impl(self, state: AgentState, use_backup: bool = False) -> dict:
        """研究节点实现（支持备用代理）"""
        print(f"---- 当前节点：{'备用' if use_backup else ''}研究节点 ----")

        # 测试代码：模拟失败
        if self.test_mode:
            node_key = "research" if not use_backup else "research_backup"
            fail_count = self.test_fail_count.get(node_key, 0)
            if fail_count < 2:  # 前两次失败
                self.test_fail_count[node_key] = fail_count + 1
                print(f"[测试模式] {node_key} 模拟失败 ({fail_count + 1}/2)")
                raise Exception(f"[测试] {node_key} 模拟执行失败")

        # 根据是否使用备用代理选择不同的提示词
        agent_name = "research_backup" if use_backup else "research"
        prompt = await self.call_mcp_tool("get_prompt", agent_name=agent_name)
        search_results = await self.call_mcp_tool("search", topic=state["topic"])

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"主题：{state['topic']}\n\n搜索结果：\n{search_results}")
        ]

        response = await self.llm.ainvoke(messages)
        report = response.content

        print("研究报告已经生成完毕。")

        error_log = state.get("error_log", [])
        new_log = state["log"] + [f"## 研究报告\n\n{report}"]

        return {
            "research_report": report,
            "log": new_log,
            "retry_count": 0,
            "error_log": error_log
        }

    async def research_node(self, state: AgentState) -> dict:
        """研究节点（带重试机制）"""
        return await self._execute_with_retry(
            "researcher",
            lambda s: self.research_node_impl(s, use_backup=False),
            lambda s: self.research_node_impl(s, use_backup=True),
            state
        )

    async def writing_node_impl(self, state: AgentState, use_backup: bool = False) -> dict:
        """撰写节点实现（支持备用代理）"""
        print(f"--- 当前节点: {'备用' if use_backup else ''}撰写节点 ---")

        # 测试代码：模拟失败
        if self.test_mode:
            node_key = "write" if not use_backup else "write_backup"
            fail_count = self.test_fail_count.get(node_key, 0)
            if fail_count < 2:  # 前两次失败
                self.test_fail_count[node_key] = fail_count + 1
                print(f"[测试模式] {node_key} 模拟失败 ({fail_count + 1}/2)")
                raise Exception(f"[测试] {node_key} 模拟执行失败")

        agent_name = "write_backup" if use_backup else "write"
        prompt_template = await self.call_mcp_tool("get_prompt", agent_name=agent_name)
        prompt = prompt_template.format(style=state["style"], length=state["length"])

        messages = [SystemMessage(content=prompt), HumanMessage(content=state["research_report"])]

        response = await self.llm.ainvoke(messages)
        draft = response.content

        print("文章草稿已经完成。")

        error_log = state.get("error_log", [])
        new_log = state["log"] + [f"## 文章草稿\n\n{draft}"]

        return {
            "draft": draft,
            "log": new_log,
            "retry_count": 0,
            "error_log": error_log
        }

    async def writing_node(self, state: AgentState) -> dict:
        """撰写节点（带重试机制）"""
        return await self._execute_with_retry(
            "writer",
            lambda s: self.writing_node_impl(s, use_backup=False),
            lambda s: self.writing_node_impl(s, use_backup=True),
            state
        )

    async def review_node_impl(self, state: AgentState, use_backup: bool = False) -> dict:
        """审核节点实现（支持备用代理）"""
        print(f"--- 当前节点: {'高级' if use_backup else ''}审核节点 ---")

        # 测试代码：模拟失败
        if self.test_mode:
            node_key = "review" if not use_backup else "review_senior"
            fail_count = self.test_fail_count.get(node_key, 0)
            if fail_count < 2:  # 前两次失败
                self.test_fail_count[node_key] = fail_count + 1
                print(f"[测试模式] {node_key} 模拟失败 ({fail_count + 1}/2)")
                raise Exception(f"[测试] {node_key} 模拟执行失败")

        agent_name = "review_senior" if use_backup else "review"
        prompt = await self.call_mcp_tool("get_prompt", agent_name=agent_name)

        messages = [SystemMessage(content=prompt), HumanMessage(content=state["draft"])]

        response = await self.llm.ainvoke(messages)
        suggestions = response.content

        print("审核完成。")

        error_log = state.get("error_log", [])
        new_log = state["log"] + [f"## 审核建议\n\n{suggestions}"]

        return {
            "review_suggestions": suggestions,
            "log": new_log,
            "retry_count": 0,
            "error_log": error_log
        }

    async def review_node(self, state: AgentState) -> dict:
        """审核节点（带重试机制）"""
        return await self._execute_with_retry(
            "reviewer",
            lambda s: self.review_node_impl(s, use_backup=False),
            lambda s: self.review_node_impl(s, use_backup=True),
            state
        )

    async def polishing_node_impl(self, state: AgentState, use_backup: bool = False) -> dict:
        """润色节点实现"""
        print(f"--- 当前节点: 润色节点 ---")

        prompt = await self.call_mcp_tool("get_prompt", agent_name="polish")
        user_input = f"文章初稿：\n\n{state['draft']}\n\n审核建议：\n\n{state['review_suggestions']}"

        messages = [SystemMessage(content=prompt), HumanMessage(content=user_input)]

        response = await self.llm.ainvoke(messages)
        final_article = response.content

        print("最终稿件完成！")

        error_log = state.get("error_log", [])
        new_log = state["log"] + [f"## 最终稿件\n\n{final_article}"]

        return {
            "final_article": final_article,
            "log": new_log,
            "retry_count": 0,
            "error_log": error_log
        }

    async def polishing_node(self, state: AgentState) -> dict:
        """润色节点（带重试机制）"""
        return await self._execute_with_retry(
            "polisher",
            lambda s: self.polishing_node_impl(s, use_backup=False),
            None,  # 润色节点没有备用代理
            state
        )

    async def _execute_with_retry(
        self,
        node_name: str,
        main_func,
        backup_func,
        state: AgentState,
        max_same_agent_retries: int = 2
    ) -> dict:
        """执行带重试策略的节点函数"""
        return await self.retry_strategy.execute_with_retry(
            node_name=node_name,
            node_func=main_func,
            state=state,
            backup_func=backup_func,
            max_same_agent_retries=max_same_agent_retries
        )
