import requests
from typing import Union
from .base import BaseLLM
import json

class MimoLLM(BaseLLM):
    def __init__(self, api_key: str, model: str, base_url: str = "https://token-plan-cn.xiaomimimo.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')

    def chat(self, input_data: Union[str, list], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": input_data,
            **kwargs
        }
        
        endpoint = f"{self.base_url}/responses"
        
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # 打印完整的原始返回体 JSON
        print("\n【API 原始返回体】:\n", json.dumps(data, indent=4, ensure_ascii=False), "\n")
        
        for item in data.get("output", []):
            if item.get("type") == "message" and item.get("role") == "assistant":
                for content_block in item.get("content", []):
                    if content_block.get("type") == "output_text":
                        return content_block.get("text", "")
        
        return ""