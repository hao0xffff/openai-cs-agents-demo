# app/providers/llm/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """
        统一的对话接口
        :param messages: 标准的消息列表，如 [{'role': 'user', 'content': '你好'}]
        :param kwargs: 其他可选参数（如 temperature, max_tokens 等）
        :return: 模型生成的文本回复
        """
        pass