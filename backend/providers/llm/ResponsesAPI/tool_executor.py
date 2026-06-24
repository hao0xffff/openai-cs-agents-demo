from typing import Any, Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """注册一个工具，name 是工具名，func 是执行函数"""
        self._tools[name] = func

    def execute(self, name: str, arguments: dict) -> str:
        """根据工具名和参数执行工具，返回字符串结果"""
        func = self._tools.get(name)
        if not func:
            return f"Error: Unknown tool '{name}'"
        try:
            result = func(**arguments)
            return str(result) if result is not None else ""
        except Exception as e:
            return f"Error executing tool '{name}': {e}"


# 全局注册器实例
global_registry = ToolRegistry()


def execute_tool_calls(tool_calls: list[dict[str, Any]], registry: ToolRegistry = None) -> list[dict[str, str]]:
    """
    执行多个 tool_call。

    参数:
        tool_calls: parse_tool_calls 返回的列表
        registry: 工具注册器，默认使用全局注册器

    返回:
        [
            {"call_id": "call_xxx", "name": "get_weather", "result": "河南今天晴天，25度"},
            ...
        ]
    """
    if registry is None:
        registry = global_registry

    results = []
    for tc in tool_calls:
        call_id = tc.get("call_id", "")
        name = tc.get("name", "")
        arguments = tc.get("arguments", {})
        result = registry.execute(name, arguments)
        results.append({
            "call_id": call_id,
            "name": name,
            "result": result,
        })
    return results
