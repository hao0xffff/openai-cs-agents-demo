import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from providers.llm.ResponsesAPI.mimo import MimoLLM
from providers.llm.ResponsesAPI.mimoparser import parse_tool_calls
from providers.llm.ResponsesAPI.tool_executor import global_registry, execute_tool_calls
from core.tool.tools import get_weather, get_news, McDonalds, KFC, Henan_Stewed_Noodles

# 1. 注册工具
global_registry.register("get_weather", get_weather)
global_registry.register("get_news", get_news)
global_registry.register("McDonald's", McDonalds)
global_registry.register("KFC", KFC)
global_registry.register("Henan_Stewed_Noodles", Henan_Stewed_Noodles)

# 2. 定义 tools 参数（告诉 LLM 有哪些工具可用）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定地点的天气",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "获取最新新闻",
            "parameters": {
                "type": "object",
                "properties": {"topic": {"type": "string"}},
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "McDonald's",
            "description": "吃麦当劳汉堡",
            "parameters": {
                "type": "object",
                "properties": {"topic": {"type": "string"}},
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "KFC",
            "description": "吃肯德基热辣香骨鸡",
            "parameters": {
                "type": "object",
                "properties": {"topic": {"type": "string"}},
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Henan_Stewed_Noodles",
            "description": "吃河南烩面",
            "parameters": {
                "type": "object",
                "properties": {"topic": {"type": "string"}},
                "required": ["topic"]
            }
        }
    },
]

# 3. 发送请求
llm = MimoLLM(api_key="tp-c6lzdivx2w1reovdamcaj7dyoqk9ycx64i42loiyqj4nqfr1", model="mimo-v2.5-pro")
res = llm.chat_raw(input_data="我要吃汉堡", tools=tools)

# 4. 解析并执行
tool_calls = parse_tool_calls(res)
print(f"解析到 {len(tool_calls)} 个工具调用")

results = execute_tool_calls(tool_calls)
for r in results:
    print(f"工具: {r['name']}, 结果: {r['result']}")
