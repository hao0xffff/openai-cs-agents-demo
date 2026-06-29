import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from core.engine import run_swarm
from core.agent import Agent
from agents.reception_agent import reception_agent

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: str = "mimo-v2.5-pro"

class ChatResponse(BaseModel):
    messages: list
    current_agent: str
    call_log: list

@app.post("/chat")
def chat(req: ChatRequest):
    """处理对话请求，执行多轮 Agent 协作"""
    current_agent = reception_agent
    messages = [{"role": "user", "content": req.message}]
    all_call_logs = []

    # 循环直到没有交接发生
    while True:
        current_agent, messages, call_log = run_swarm(
            starting_agent=current_agent,
            messages=messages,
            model=req.model,
            verbose=True
        )
        all_call_logs.extend(call_log)

        # 检查是否发生了交接（检查最后一条消息是否是 tool 类型的交接提示）
        last_msg = messages[-1]
        if isinstance(last_msg, dict) and last_msg.get("role") == "tool":
            # 发生了交接，继续循环
            continue
        else:
            # 没有交接，检查是否调用了工具
            break

    # 为每个 assistant 消息标注来源 agent
    annotated_messages = []
    assistant_idx = 0
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            # 找到对应的 agent（按顺序匹配）
            if assistant_idx < len(all_call_logs):
                msg = dict(msg)  # 复制一份
                msg["agent"] = all_call_logs[assistant_idx]["agent"]
            assistant_idx += 1
        annotated_messages.append(msg)

    return ChatResponse(
        messages=annotated_messages,
        current_agent=current_agent.name,
        call_log=all_call_logs
    )

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)