import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from providers.llm.ResponsesAPI.mimo import MimoLLM
from providers.llm.ResponsesAPI.mimoparser import parse_tool_calls

def main():
    api_key = "tp-c6lzdivx2w1reovdamcaj7dyoqk9ycx64i42loiyqj4nqfr1"
    model_name = "mimo-v2.5-pro" # 根据实际情况替换
    
    llm = MimoLLM(api_key=api_key, model=model_name)
    
    input_text = "我要查河南天气！"

    # 1. 定义工具
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定地点的天气信息",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"]
            }
        }
    }]
    
    print("正在发送新版请求...")
    try:
        res = llm.chat_raw(input_data=input_text,tools=tools)
        print("回复:", res)
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(parse_tool_calls(res))
    except Exception as e:
        print("报错:", e)

if __name__ == "__main__":
    main()