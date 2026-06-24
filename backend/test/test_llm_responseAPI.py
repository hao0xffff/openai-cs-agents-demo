import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from providers.llm.ResponsesAPI.mimo import MimoLLM

def main():
    api_key = "tp-c6lzdivx2w1reovdamcaj7dyoqk9ycx64i42loiyqj4nqfr1"
    model_name = "mimo-v2.5-pro" # 根据实际情况替换
    
    llm = MimoLLM(api_key=api_key, model=model_name)
    
    input_text = "Write a one-sentence bedtime story about a unicorn."
    
    print("正在发送新版请求...")
    try:
        res = llm.chat(input_data=input_text)
        print("回复:", res)
    except Exception as e:
        print("报错:", e)

if __name__ == "__main__":
    main()