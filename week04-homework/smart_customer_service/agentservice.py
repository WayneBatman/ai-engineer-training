from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import PromptTemplate

import config
from tools import *


class AgentService:

    def __init__(self):
        print("初始化核心服务")
        self._model = self._create_model()
        self._system_msg = self._init_system_msg()
        self._tools = self._init_tools()
        self._agent = self._create_agent()
        print("核心服务初始化成功")

    def _create_model(self):
        if not config.DASHSCOPE_API_KEY:
            raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

        return ChatTongyi(
            model=config.LLM_MODEL_NAME
        )

    def _init_system_msg(self):
        system_prompt = PromptTemplate.from_template(
            """
            你的唯一身份是{assistant_name}，不是其他任何名称（包括Qwen、通义千问等）。
            日常回复开头需以{assistant_name}的身份回应，禁止提及Qwen、通义千问等相关名称。
            基础话术：您好，我是{assistant_name},我是您的智能客服助手，有什么可以帮助你？
            如果工具返回的信息，必须结合工具返回的信息，生成最后的回复
            """
        )
        system_msg =system_prompt.format(assistant_name=config.ASSISTANT_NAME)
        return system_msg

    def _init_tools(self) -> list:
        return [
            get_date_from_question
        ]

    def _create_agent(self):
        agent = create_agent(
            model=self._model,
            system_prompt=self._system_msg,
            tools=self._tools,
            debug = config.DEBUG_MODE
        )
        return agent

    # def print_services(self):
    #     print("--- 当前服务状态 ---")
    #     print(f"  模型: {self._llm.model_name}")
    #     print(f"  工具: {[tool.name for tool in self._tools]}")
    #     print("--------------------")

    def get_services_status(self):
        return {
            "model": self._model.model_name,
            "status": self._model.status
        }

    def chat_response(self,question:str):
        human_message = HumanMessage(content=[
            {"type": "text", "text": question},
        ])

        response = self._agent.invoke({
            "messages": [human_message]
        })

        # response = self._agent.invoke(
        #     {"messages": [{"role": "user", "content": question }]}
        # )

        print("当前系统回复：",response)
        # 这里使用-1 是因为使用系统提示词，限制LLM的回复
        #final_message = response['messages'][-1]
        # 实际上，如果工具返回的message，则应该以toolMessage为准

        reply = response['messages'][-1].content
        for message in response["messages"]:
            if(isinstance(message,ToolMessage)):
                reply = message.content
                break

        return reply


# 创建一个单例
service_manager = AgentService()