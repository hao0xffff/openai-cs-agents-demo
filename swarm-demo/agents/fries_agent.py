from core.agent import Agent

def make_fries():
    """工具函数：后厨炸薯条的具体操作"""
    return "🍟 系统提示：热腾腾的薯条炸好了！"

fries_agent = Agent(
    name="炸薯条师傅",
    instructions="你是麦当劳后厨的炸薯条师傅。收到任务后，你必须调用 make_fries 工具，并热情地告诉顾客薯条已经准备好了。",
    functions=[make_fries]
)