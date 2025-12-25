from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

def llm_tongyi_init():
    llm = Tongyi()
    #llm.invoke()方式是标准的方式
    print(llm.invoke("您好"))
    #下面这个方式，现在的tongyi版本已经不支持这么直接调用了
    #print(llm("你好，今天的金价是多少钱？"))

def llm_deepseek_init():
    deepseek_llm = ChatDeepSeek(model="deepseek-chat")
    print(deepseek_llm.invoke("您好"))

def llm_prompt_test():
    llm = Tongyi()
    prompt = PromptTemplate.from_template(
        "你好，我是{model_name}，需要我的帮助么？"
    )
    msg = prompt.format(model_name="qianwen-chat")
    print(msg)

def llm_message_test():
    chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的AI助手 {assistant_name}."),
    ("human", "你好，我是 {user_name}.我的问题是{question}")
    ])

    messages = chat_prompt.format_messages(
        assistant_name = '小菱',
        user_name = 'Wayne',
        question = '今天黄埔的天气怎么样？'
    )

    for message in messages:
        print(f"{message.type}: {message.content}")

def llm_complex_prompt_test():
    complex_prompt = PromptTemplate(
        input_variables=['topic','audience','tone'],
        template="""
            请为{audience}写一篇关于{topic}的文章。
            写作风格应该是{tone}的。
            
            文章要求：
            - 内容准确且有用
            - 结构清晰
            - 适合目标受众
        """
    )

    result = complex_prompt.format(
        topic="人工智能",
        audience="初学者",
        tone="通俗易懂"
    )

    print(result)
def llm_f_string_prompt_test():
    f_string_prompt = PromptTemplate.from_template(
        "分析以下{data_type}数据：\n{data}\n\n请提供{analysis_type}分析。"
    )

    result = f_string_prompt.format(
        data_type="销售",
        data="Q1销售额: 100万, Q2销售额: 120万",
        analysis_type="趋势"
    )
    print(result)

def main():
    #llm_tongyi_init()
    #llm_deepseek_init()
    #llm_prompt_test()
    #llm_message_test()
    #llm_complex_prompt_test()
    llm_f_string_prompt_test()


if __name__ == "__main__":
    main()
