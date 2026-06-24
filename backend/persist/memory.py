# app/persist/memory.py
from typing import List, Dict, Any
from core.context.context import BaseMemoryStore

class DictMemoryStore(BaseMemoryStore):
    """
    基于字典的内存会话存储（仅用于本地快速测试）
    系统重启后数据会丢失
    """
    def __init__(self):
        # 数据结构: { "session_id_1": [ msg1, msg2... ], "session_id_2": [...] }
        self.storage: Dict[str, List[Dict[str, Any]]] = {}

    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        if session_id not in self.storage:
            self.storage[session_id] = []
        self.storage[session_id].append(message)

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        history = self.storage.get(session_id, [])
        # 如果设置了限制，则只截取最近的 limit 条消息，防止超出模型 Token 限制
        if limit > 0:
            return history[-limit:]
        return history

    def clear(self, session_id: str) -> None:
        if session_id in self.storage:
            self.storage[session_id] = []