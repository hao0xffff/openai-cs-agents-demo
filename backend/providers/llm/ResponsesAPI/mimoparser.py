import json
from typing import Any, Union


def parse_tool_calls(response: Union[dict, str]) -> list[dict[str, Any]]:
    """
    从 Mimo API 响应中解析出所有 tool_call 信息。

    返回格式:
        [
            {
                "id": "fc_1312a1b3252e491184473a1777f2dc73",
                "call_id": "call_f01358dbb0294e00ad02cabb",
                "name": "get_weather",
                "arguments": {"location": "河南"}
            }
        ]
    """
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            return []

    tool_calls = []
    for item in response.get("output", []):
        if item.get("type") == "function_call":
            tool_calls.append({
                "id": item.get("id"),
                "call_id": item.get("call_id"),
                "name": item.get("name"),
                "arguments": _parse_arguments(item.get("arguments", "{}")),
            })
    return tool_calls


def _parse_arguments(arguments_str: str) -> dict:
    try:
        return json.loads(arguments_str)
    except (json.JSONDecodeError, TypeError):
        return {}
