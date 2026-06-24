# app/core/agent.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        name: str,
        system_prompt: str,
        llm: Any,  # 这里后续会注入声明的 BaseLLM 实例
        tools: Optional[List[Any]] = None  # 后续注入 BaseTool 实例列表
    ):
        """
        Agent 核心基类
        :param agent_id: 唯一标识符，对应数据库中的持久化 ID
        :param name: Agent 的名称（如 'Flight_Data_Agent'）
        :param system_prompt: 核心系统提示词，决定 Agent 的人设与边界
        :param llm: 注入的底层大模型实例（屏蔽了厂商接口差异）
        :param tools: 该 Agent 拥有权限调用的工具列表
        """
        self.agent_id = agent_id
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm
        self.tools = tools or []
        self.tool_map = {tool.name: tool for tool in self.tools}

    @abstractmethod
    def execute(self, session_id: str, user_input: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        单次决策的执行入口（由编排器调度）
        :param session_id: 当前会话 ID（用于追溯记忆）
        :param user_input: 用户本次的输入文本
        :param history: 过滤并组装好的历史上下文列表
        :return: 统一的决策结果字典。例如：
                 成功回复: {"status": "success", "content": "回复内容"}
                 请求工具: {"status": "tool_call", "tool_name": "...", "args": {...}}
                 移交控制: {"status": "handoff", "target_agent": "agent_id"}
        """
        pass