# app/core/tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        """
        工具核心基类
        :param name: 工具的唯一名称 (供 LLM 调用，要求只能是字母、数字和下划线，如 'get_flight_status')
        :param description: 工具的功能描述 (重要提示词，指导 LLM 在什么场景下使用该工具)
        :param parameters: 工具的入参结构 (遵循标准的 JSON Schema 规范)
        """
        self.name = name
        self.description = description
        self.parameters = parameters

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        工具的具体业务执行逻辑
        :param kwargs: 运行时由大模型解析并传入的具体参数
        :return: 工具的执行结果（必须能够被序列化为字符串，以便返回给大模型）
        """
        pass

    def to_llm_format(self) -> Dict[str, Any]:
        """
        转换为大模型 (OpenAI 标准) 能够直接识别的工具描述格式
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }