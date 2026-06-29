from core.agent import Agent

def pour_cola():
    """工具函数：后厨倒可乐的具体操作"""
    return "🥤 系统提示：冰可乐倒好了，加了冰块！"

cola_agent = Agent(
    name="倒可乐专员",
    instructions="你是麦当劳后厨的水吧专员。收到任务后，你必须调用 pour_cola 工具，并热情地告诉顾客可乐准备好了。",
    functions=[pour_cola]
)