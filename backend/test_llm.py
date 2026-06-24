# python-backend/test_llm.py
from providers.llm.ChatCompletionsAPI.mimo import MimoLLM

def test_mimo():
    # TODO: 替换为你真实的 Mimo API Key 和 API 地址
    api_key = "tp-c6lzdivx2w1reovdamcaj7dyoqk9ycx64i42loiyqj4nqfr1" 
    base_url = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions" # 请查阅 Mimo 文档替换真实 URL

    llm = MimoLLM(api_key=api_key, base_url=base_url)

    messages = [
        {"role": "user", "content": "你好，请自我介绍一下。"}
    ]

    print("正在请求 Mimo 大模型...")
    try:
        response_text = llm.chat(messages=messages)
        print("\n--- Mimo 回复 ---")
        print(response_text)
    except Exception as e:
        print(f"\n请求失败: {e}")

if __name__ == "__main__":
    test_mimo()