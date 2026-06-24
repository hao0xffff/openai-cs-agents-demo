# app/core/context.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMemoryStore(ABC):
    """
    记忆存储的抽象基类（定义了持久化契约）
    """
    @abstractmethod
    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """向指定会话追加一条消息"""
        pass

    @abstractmethod
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取指定会话的历史记录"""
        pass

    @abstractmethod
    def clear(self, session_id: str) -> None:
        """清空会话记忆"""
        pass


class ContextManager:
    """
    会话上下文管理器
    负责组装消息格式、调用存储层，并可在此扩展“超出限制自动截断/总结”的策略
    """
    def __init__(self, memory_store: BaseMemoryStore):
        self.store = memory_store

    def append_user_message(self, session_id: str, content: str):
        self.store.add_message(session_id, {"role": "user", "content": content})

    def append_agent_message(self, session_id: str, content: str):
        self.store.add_message(session_id, {"role": "assistant", "content": content})
        
    def append_tool_result(self, session_id: str, tool_name: str, result_content: str):
        # 组装标准的大模型工具返回格式
        self.store.add_message(session_id, {
            "role": "tool", 
            "name": tool_name, 
            "content": result_content
        })

    def get_context(self, session_id: str, max_messages: int = 20) -> List[Dict[str, Any]]:
        """
        获取组装好的上下文
        未来可在此处增加 Token 计算、滑动窗口或摘要逻辑
        """
        return self.store.get_history(session_id, limit=max_messages)