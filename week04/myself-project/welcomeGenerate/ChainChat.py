from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


class ChatChain:
    def __init__(self):
        self.llm = None
        self.chain = None
        self.prompt = None
        self.parser = StrOutputParser()

    async def initialize(self):
        #初始化大模型
        self.llm = Tongyi()

    async def generate_prompt(self,name:str):
        self.prompt = PromptTemplate.from_template(
            "您好，{name}，欢迎使用智能客服"
        )
        msg = self.prompt.format(name=name)
        print(msg)
        return msg