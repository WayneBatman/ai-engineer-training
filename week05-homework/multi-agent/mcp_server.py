import json
from fastmcp import FastMCP
from duckduckgo_search import DDGS
import angent_prompts as PROMPTS


mcp = FastMCP("文章Agent工具")


@mcp.tool
def search(topic: str, max_results: int = 5) -> str:
    """根据主题进行网络搜索，并返回JSON格式的搜索结果。"""
    print(f"MCP服务器: 执行搜索： '{topic}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=max_results))
            return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool
def get_prompt(agent_name: str) -> str:
    """根据代理名称获取对应的系统提示词。"""
    print(f"MCP服务器: 获取提示词： '{agent_name}'...")
    print(f"PROMPTS type: {type(PROMPTS)}")
    print(f"PROMPTS keys: {dir(PROMPTS) if hasattr(PROMPTS, '__dict__') else 'N/A'}")
    print(f"PROMPTS dict: {PROMPTS.__dict__ if hasattr(PROMPTS, '__dict__') else PROMPTS}")
    return PROMPTS.PROMPTS.get(agent_name, f"Error: 获取提示词失败. agent_name={agent_name}")


def run():
    """运行 FastMCP HTTP 服务。"""
    print("MCP服务器 (HTTP) 运行了  http://localhost:8000/mcp")
    # 使用 streamable-http 传输方式
    mcp.run(transport="streamable-http", port=8000)


if __name__ == "__main__":
    run()
