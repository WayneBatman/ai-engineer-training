from langgraph.graph import MessagesState, StateGraph,START,END
from IPython.display import Image, display


def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

def main():

    graph = StateGraph(MessagesState)
    graph.add_node(mock_llm)
    graph.add_edge(START, "mock_llm")
    graph.add_edge("mock_llm", END)
    graph = graph.compile()

    # 核心修改：将流程图保存到本地（指定路径，如当前目录的graph.png）
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")  # 保存到本地，文件名graph.png
    print("流程图已保存到本地：graph.png")

    # （可选）若需要预览，再读取保存的文件
    # display(Image.open("graph.png"))

    result =graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
    print(result)

if __name__ == '__main__':
    main()