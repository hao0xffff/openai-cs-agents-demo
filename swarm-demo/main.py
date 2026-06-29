from core.engine import run_swarm
from agents.reception_agent import reception_agent

def main():
    print("🍔 欢迎来到手搓版麦当劳 Agent 模拟系统 (输入 'quit' 退出)")
    
    current_agent = reception_agent
    messages = []

    while True:
        user_input = input("\n顾客: ")
        if user_input.lower() == 'quit':
            break
            
        messages.append({"role": "user", "content": user_input})

        # 新增内部循环：如果发生交接，引擎会自动带着新 Agent 继续请求，直到回答完毕
        while True:
            new_agent, messages = run_swarm(
                starting_agent=current_agent,
                messages=messages,
                model="mimo-v2.5-pro" 
            )
            
            # 如果 Agent 没变，说明交接和处理全部完毕，跳出内部循环
            if new_agent.name == current_agent.name:
                break
                
            # 如果 Agent 变了，更新当前 Agent 继续让它接话
            current_agent = new_agent
            
        # 安全读取最后一条大模型回复（兼容对象或字典格式）
        last_msg = messages[-1]
        content = last_msg.content if not isinstance(last_msg, dict) else last_msg.get("content")
        print(f"\n{current_agent.name}: {content}")

if __name__ == "__main__":
    main()