import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 里的环境变量
load_dotenv()

# 初始化并暴露 client 实例
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)