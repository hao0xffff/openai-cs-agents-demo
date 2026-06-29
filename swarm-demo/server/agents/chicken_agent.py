from core.agent import Agent

def make_chicken():
    """工具函数：后厨炸鸡的具体操作"""
    return "🍗 系统提示：金黄酥脆的炸鸡出锅了！"

chicken_agent = Agent(
    name="炸鸡师傅",
    instructions="你是麦当劳后厨的炸鸡师傅。收到任务后，你必须调用 make_chicken 工具，并热情地告诉顾客炸鸡准备好了。",
    functions=[make_chicken]
)