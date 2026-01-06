from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage

import angent_state as AgentState

class ArticleAgentNode:
    def __init__(self, mcp_tools: list):
        self.mcp_tools = {tool.name: tool for tool in mcp_tools}
        self.llm = ChatTongyi(model="qwen-max")

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

    async def research_node(self, state: AgentState) -> dict:
        print("---- 当前节点：研究节点 ----")
        prompt = await self.call_mcp_tool("get_prompt", agent_name="research")
        search_results = await self.call_mcp_tool("search", topic=state["topic"])
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"主题：{state['topic']}\n\n搜索结果：\n{search_results}")
        ]
        response = await self.llm.ainvoke(messages)
        report = response.content
        print("研究报告已经生成完毕。")
        return {"research_report": report, "log": state["log"] + [f"## 研究报告\n\n{report}"]}

    async def writing_node(self, state: AgentState) -> dict:
        print("--- 当前节点: 撰写节点 ---")
        prompt_template = await self.call_mcp_tool("get_prompt", agent_name="write")
        prompt = prompt_template.format(style=state["style"], length=state["length"])
        messages = [SystemMessage(content=prompt), HumanMessage(content=state["research_report"])]
        response = await self.llm.ainvoke(messages)
        draft = response.content
        print("文章草稿已经完成。")
        return {"draft": draft, "log": state["log"] + [f"## 文章草稿\n\n{draft}"]}

    async def review_node(self, state: AgentState) -> dict:
        print("--- 当前节点: 审核节点 ---")
        prompt = await self.call_mcp_tool("get_prompt", agent_name="review")
        messages = [SystemMessage(content=prompt), HumanMessage(content=state["draft"])]
        response = await self.llm.ainvoke(messages)
        suggestions = response.content
        print("审核完成。")
        return {"review_suggestions": suggestions, "log": state["log"] + [f"## 审核建议\n\n{suggestions}"]}

    async def polishing_node(self, state: AgentState) -> dict:
        print("--- 当前节点: 润色 ---")
        prompt = await self.call_mcp_tool("get_prompt", agent_name="polish")
        user_input = f"文章初稿：\n\n{state['draft']}\n\n审核建议：\n\n{state['review_suggestions']}"
        messages = [SystemMessage(content=prompt), HumanMessage(content=user_input)]
        response = await self.llm.ainvoke(messages)
        final_article = response.content
        print("最终稿件完成！")
        return {"final_article": final_article}
