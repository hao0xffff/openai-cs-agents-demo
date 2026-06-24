from abc import ABC, abstractmethod
from typing import Union, Any

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, input_data: Union[str, list], **kwargs) -> str:
        pass