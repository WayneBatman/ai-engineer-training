from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState,START,END
from langgraph.prebuilt import ToolNode

from agentservice import AgentService

class GraphManager:
    def __init__(self,service_manager: AgentService):
        self.service_manager = service_manager
        self._app = self._build_graph()

    def _build_graph(self):
        # 构建工作流
        agent_builder = StateGraph(MessagesState)

        tools = self.service_manager.get_tools()
        tool_node = ToolNode(tools)

        # 添加节点
        agent_builder.add_node("agent", self._call_model)
        agent_builder.add_node("tool_node", tool_node)
        agent_builder.add_node("ask_for_order_id", self._ask_for_order_id)

        # 添加边来连接节点
        agent_builder.set_conditional_entry_point(
            self._router,#_router（路由函数仅用于条件分支，无需作为节点）；
            path_map={
                "ask_for_order_id": "ask_for_order_id",
                "agent": "agent",
            }
        )
        agent_builder.add_edge('ask_for_order_id', END)
        agent_builder.add_conditional_edges(
            "agent",
            self._should_continue,
            {"tool_node": "tool_node", "end": END}
        )
        agent_builder.add_edge("tool_node", "agent")

        # 编译智能体
        agent = agent_builder.compile()
        return agent

    #_router（路由函数仅用于条件分支，无需作为节点）；
    def _router(self,state: MessagesState) -> Literal["agent", "ask_for_order_id"]:
        print("--- [Node] Router: 分析用户意图 ---")
        last_message = state['messages'][-1]
        response = "已收到你的问题，我正在处理中..."
        # 简单的关键词匹配路由，未来可以替换为更复杂的意图识别模型
        if "查订单" in last_message.content and "SN" not in last_message.content:
            # 如果用户提到了相对时间，也交给agent处理
            if any(kw in last_message.content for kw in ["昨天", "前天", "今天", "上周"]):
                 return "agent"
            print("--- [Decision] 路由到 'ask_for_order_id'. ---")
            return "ask_for_order_id"
        else:
            print("--- [Decision] 路由到 to 'agent'. ---")
            return "agent"

    def _call_model(self, state: MessagesState):
        """
        直接调用大模型+工具的方式来处理
        """
        print("--- [Node] Agent: Thinking... ---")
        try:
            llm = self.service_manager.get_model()
            tools = self.service_manager.get_tools()
            model_with_tools = llm.bind_tools(tools)
            response = model_with_tools.invoke(state['messages'])
            return {"messages": [response]}
        except Exception as e:
            print(f"模型调用错误: {e}")
            return {"messages": [AIMessage(content="抱歉，系统出现错误，请稍后再试。")]}

    def _call_agent(self,state: MessagesState):
        pass

    def _should_continue(self,state: MessagesState) -> Literal["tool_node", "end"]:
        last_message = state['messages'][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            print("--- [Decision] LLM requested a tool call, routing to tool node. ---")
            return "tool_node"
        print("--- [Decision] No tool call, ending turn. ---")
        return "end"

    def _ask_for_order_id(self,state: MessagesState):
        print("--- [Node] ask_for_order_id: Generating a follow-up question. ---")
        follow_up_message = AIMessage(content="好的，请问您的订单号是多少？")
        return {"messages": [follow_up_message]}

    def get_app(self):
        """获取编译好的 LangGraph 应用实例"""
        return self._app

    def chat_response(self, question,user_id):
        """与智能客服进行单轮对话"""
        thread_id = user_id
        config = {"configurable": {"thread_id": thread_id}}

        messages = [HumanMessage(content=question)]


        final_response = ""
        # 流式处理以获取最终回复
        for event in self._app.stream({"messages": messages}, config=config, stream_mode="values"):
            if "messages" in event:
                last_message = event["messages"][-1]
                if isinstance(last_message, AIMessage) and not last_message.tool_calls:
                    final_response = last_message.content

        if not final_response:
            return {"user_id": thread_id, "response": "抱歉，我暂时无法回答这个问题。"}

        return {"user_id": thread_id, "response": final_response}