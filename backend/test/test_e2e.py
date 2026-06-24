# test_e2e.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from providers.llm.ResponsesAPI.mimo import MimoLLM
from core.agent.agent import BaseAgent
from core.orchestrator.orchestrator import Orchestrator
from core.context.context import ContextManager
from persist.memory import DictMemoryStore

# 1. 实现一个具体的测试 Agent
class SimpleChatAgent(BaseAgent):
    def execute(self, session_id: str, user_input: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 组装消息列表 (System Prompt + History + Current Input)
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        
        try:
            # 调用底层 LLM (注意我们之前改版后 mimo 用的是 input_data)
            reply = self.llm.chat(input_data=messages)
            return {"status": "success", "content": reply}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def main():
    # 2. 初始化核心底座组件
    api_key = "tp-c6lzdivx2w1reovdamcaj7dyoqk9ycx64i42loiyqj4nqfr1" # 请确认密钥有效
    model_name = "mimo-v2.5-pro"
    
    llm = MimoLLM(api_key=api_key, model=model_name)
    memory_store = DictMemoryStore()
    context_manager = ContextManager(memory_store)
    
    # 3. 实例化 Agent 并注册到编排器
    agent1 = SimpleChatAgent(
        agent_id="agent_001",
        name="TestBot",
        system_prompt="你是一个幽默的AI助手，回答总是简短且带点冷幽默。",
        llm=llm
    )
    
    orchestrator = Orchestrator(agents=[agent1], default_agent_id="agent_001")
    session_id = "test_session_999"

    print("=== Agent 编排底座测试启动 (输入 'quit' 退出) ===")
    
    # 4. 模拟 Web API 或 WebSocket 的轮询接收入口
    while True:
        user_input = input("\n用户: ")
        if user_input.strip().lower() == 'quit':
            break
            
        # 4.1 获取历史上下文
        history = context_manager.get_context(session_id, max_messages=5)
        
        # 4.2 交给编排器进行调度决策
        result = orchestrator.dispatch(session_id, user_input, history)
        
        # 4.3 处理调度结果，并持久化记忆
        if result["status"] == "success":
            reply = result["content"]
            print(f"\nAgent [{result['active_agent_id']}]: {reply}")
            
            # 对话成功，双向追加到上下文中
            context_manager.append_user_message(session_id, user_input)
            context_manager.append_agent_message(session_id, reply)
            
        elif result["status"] == "error":
            print(f"\n[系统错误]: {result['message']}")
            break

if __name__ == "__main__":
    main()