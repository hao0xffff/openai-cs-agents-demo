# app/core/orchestrator.py
from typing import List, Dict, Any, Optional
from core.agent.agent import BaseAgent

class Orchestrator:
    def __init__(self, agents: List[BaseAgent], default_agent_id: str, max_turns: int = 10):
        """
        多 Agent 编排调度器
        :param agents: 系统中所有可用的 Agent 实例列表
        :param default_agent_id: 默认的入口 Agent ID（主接待/网关 Agent）
        :param max_turns: 单次请求最大流转轮数，防止 Agent 之间发生无限死循环移交
        """
        self.agents_map = {agent.agent_id: agent for agent in agents}
        self.default_agent_id = default_agent_id
        self.max_turns = max_turns

    def dispatch(
        self, 
        session_id: str, 
        user_input: str, 
        history: List[Dict[str, Any]], 
        current_agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        核心调度循环分发器
        :param session_id: 当前会话 ID
        :param user_input: 用户本次输入的文本
        :param history: 历史对话上下文
        :param current_agent_id: 当前处于激活状态的 Agent ID，如果首次进入则为 None
        :return: 最终决策或中断状态字典
        """
        active_agent_id = current_agent_id or self.default_agent_id
        turns = 0
        
        while turns < self.max_turns:
            turns += 1
            agent = self.agents_map.get(active_agent_id)
            if not agent:
                return {"status": "error", "message": f"Agent [{active_agent_id}] 未注册"}
            
            # 让当前激活的 Agent 做出决策
            result = agent.execute(session_id, user_input, history)
            
            # 情况 1：Agent 成功给出了最终回复，或者内部发生错误，直接返回给上层
            if result["status"] in ["success", "error"]:
                return {**result, "active_agent_id": active_agent_id}
                
            # 情况 2：Agent 决定移交控制权 (Handoff)给另一个 Agent
            elif result["status"] == "handoff":
                target_agent_id = result["target_agent"]
                # 变更当前激活的 Agent，进入下一轮循环让新的 Agent 接管
                active_agent_id = target_agent_id
                continue
                
            # 情况 3：Agent 决定调用工具 (Tool Call)
            elif result["status"] == "tool_call":
                # 为了保持编排器的纯粹和高内聚，将工具执行的中断信号抛给更上层（如 API 或 业务层）
                # 外部执行完具体工具代码并追加历史后，再次调用 dispatch 推进状态机
                return {**result, "active_agent_id": active_agent_id}
                
        return {"status": "error", "message": "超出了最大流转轮数限制，流转链路可能存在死循环"}