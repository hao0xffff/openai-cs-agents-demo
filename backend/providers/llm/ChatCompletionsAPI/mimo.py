# app/providers/llm/mimo.py
import requests
from typing import List, Dict, Any
from .base import BaseLLM

class MimoLLM(BaseLLM):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mimo-v2.5-pro",
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]