import json
from core.client import client
from core.agent import Agent

def run_swarm(starting_agent: Agent, messages: list, model: str, verbose: bool = False):
    """手搓的核心调度引擎

    Args:
        starting_agent: 起始 Agent
        messages: 消息历史
        model: 模型名称
        verbose: 是否记录详细调用信息

    Returns:
        (current_agent, current_messages, call_log) - 如果 verbose=True
        (current_agent, current_messages) - 如果 verbose=False
    """
    current_agent = starting_agent
    current_messages = messages.copy()
    call_log = [] if verbose else None

    # 1. 组装系统提示词
    api_messages = [{"role": "system", "content": current_agent.instructions}] + current_messages

    # 2. 简易封包：把 Python 函数转换成大模型认识的 tools 格式
    tools = []
    function_map = {}
    for func in current_agent.functions:
        tools.append({
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "工具函数"
            }
        })
        function_map[func.__name__] = func

    # 3. 发送请求给大模型
    request_payload = {
        "model": model,
        "messages": api_messages,
        "tools": tools if tools else None
    }

    response = client.chat.completions.create(
        model=model,
        messages=api_messages,
        tools=tools if tools else None
    )

    response_message = response.choices[0].message
    # 转换为字典格式，确保可序列化
    response_dict = response_message.model_dump() if hasattr(response_message, 'model_dump') else {"role": "assistant", "content": str(response_message)}
    current_messages.append(response_dict) # 记录模型回复

    # 记录调用详情
    if verbose:
        tool_calls_info = []
        if response_dict.get("tool_calls"):
            for tc in response_dict["tool_calls"]:
                tool_calls_info.append({
                    "function_name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"]
                })
        call_log.append({
            "agent": current_agent.name,
            "agent_instructions": current_agent.instructions,
            "request": request_payload,
            "response": response.model_dump() if hasattr(response, 'model_dump') else str(response),
            "tool_calls": tool_calls_info
        })

    # 4. 【核心交接逻辑】判断大模型有没有调用工具
    if response_dict.get("tool_calls"):
        for tool_call in response_dict["tool_calls"]:
            func_name = tool_call["function"]["name"]
            func_to_call = function_map.get(func_name)

            if func_to_call:
                # 执行你的 Python 函数 (比如 transfer_to_order)
                result = func_to_call()

                # ！！！Handoff 灵魂判断 ！！！
                # 如果函数返回的是一个 Agent 对象，说明发生了交接
                # ！！！Handoff 灵魂判断 ！！！
                if isinstance(result, Agent):
                    print(f"\n🔄 [系统底层] 发生交接: {current_agent.name} 移交给 -> {result.name}\n")

                    # 【新增】必须把交接动作告诉大模型，修复上下文断层
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": func_name,
                        "content": f"系统提示：已成功交接给 {result.name}，请新Agent接手处理。"
                    })

                    # 返回时带上 call_log
                    return result, current_messages, call_log

                # 如果只是普通工具(比如查库存)，记录结果，这里为了精简 Demo 就不做二次递归了
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": func_name,
                    "content": str(result)
                })

    # 返回时带上 call_log（如果没有发生交接，call_log 只有一个元素）
    return current_agent, current_messages, call_log