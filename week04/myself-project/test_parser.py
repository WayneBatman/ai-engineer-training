from langchain_community.llms.tongyi import Tongyi
from langchain_core.output_parsers import PydanticOutputParser, CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field


# class PersonInfo(BaseModel):
#     name: str = Field(description="姓名")
#     age: int = Field(description="年龄")
#     occupation: str = Field(description="职业")

def test_parser():
    parser = CommaSeparatedListOutputParser()

    raw_output = "Python, Java, JavaScript, C++, Go"

    # 解析输出
    parsed_result = parser.parse(raw_output)
    print("手动解析结果:", parsed_result)

def simple_list_generation(category):
    parser = CommaSeparatedListOutputParser()
    prompt = f"""
            请列出5个{category}的例子
            {parser.get_format_instructions()}    
            """
    llm = Tongyi()

    response = llm.invoke(prompt)
    print(response)
    return parser.parse(response)

def test_comma_separated_list_parser():
    # 1.创建输出解析器
    parser = CommaSeparatedListOutputParser()

    # 2.获取格式化指令
    format_instructions =  parser.get_format_instructions()
    print("格式化指令:", format_instructions)

    #3.创建包含格式指令的提示模板
    prompt = PromptTemplate(
        template="请列出5个{category}的例子。\n{format_instructions}",
        input_variables = ["category"],
        partial_variables = {"format_instructions": format_instructions}
    )
    #4.初始化LLM
    llm = Tongyi()
    # 5. 创建完整的链
    chain = prompt | llm | parser

    #6.使用示例
    try:
        result = chain.invoke({"category": "水果"})
        print("解析后的结果:", result)
        print("结果类型：", type(result))

        for i,language in enumerate(result,1):
            print(f"{i}. {language}")
    except Exception as e:
        print(f"解析错误: {e}")


    categories = ["编程语言","运动项目","乐器"]

    for category in categories:
        print(f"\n==={category}===")
        try:
            result = chain.invoke({"category": category})
            for item in result:
                print(f"{item}")
        except Exception as e:
            print(f"处理{category}时出错:{e}")

def test_shop_list():
    # 1.初始化输出解析器
    parser = CommaSeparatedListOutputParser()
    format_instructions = parser.get_format_instructions()
    # 2.初始化大模型
    llm = Tongyi()
    # 3.创建提示词模板
    shopping_prompt = PromptTemplate(
        template="根据{meal_type},生成一个包含5个食材的购物清单。\n{format_instructions}",
        input_variables = ["meal_type"],
        partial_variables = {"format_instructions": format_instructions}
    )

    #4.创建调用
    shopping_chain = shopping_prompt | llm | parser

    #5.生成购物清单
    meals = ["早餐","午餐","晚餐"]
    shopping_list = {}

    for meal in meals:
        shopping_list[meal] = shopping_chain.invoke({"meal_type": meal})
        print(f"{meal}购物清单:{shopping_list[meal]}")

    print("++++详细的购物清单++++")
    for meal, items in shopping_list.items():
        print(f"\n🍽️ {meal}:")
        for i,item in enumerate(items,1):
            print(f"{i}. {item}")

def test_multiply_list():
    parser = CommaSeparatedListOutputParser();

    chain = (
            PromptTemplate(
                template="请列出5个{category}的{item_type}。\n{format_instructions}",
                input_variables = ["category", "item_type"],
                partial_variables = {"format_instructions": parser.get_format_instructions()}
            )
             |Tongyi()
             |parser
    )

    # 多场景使用
    scenarios = [
        {"category": "早餐", "item_type": "食材"},
        {"category": "办公室", "item_type": "用品"},
        {"category": "旅行", "item_type": "必需品"},
        {"category": "健身", "item_type": "器材"},
        {"category": "学习", "item_type": "工具"}
    ]

    for scenario in scenarios:
        result = chain.invoke(scenario)
        print(f"{scenario['category']}{scenario['item_type']}:{result}")





def main():
    #test_parser()
    # fruits = simple_list_generation("水果")
    # print("水果列表:", fruits)
    #
    # languages = simple_list_generation("编程语言")
    # print("编程语言列表:", languages)

    #test_comma_separated_list_parser()
    #test_shop_list()
    test_multiply_list()

if __name__ == '__main__':
    main()