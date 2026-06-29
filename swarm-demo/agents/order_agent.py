from core.agent import Agent
from agents.fries_agent import fries_agent
from agents.chicken_agent import chicken_agent
from agents.cola_agent import cola_agent

def transfer_to_fries():
    """交接函数：当顾客要点薯条时，交接给炸薯条师傅"""
    return fries_agent

def transfer_to_chicken():
    """交接函数：当顾客要点炸鸡或麦乐鸡时，交接给炸鸡师傅"""
    return chicken_agent

def transfer_to_cola():
    """交接函数：当顾客要点可乐或饮料时，交接给倒可乐专员"""
    return cola_agent

order_agent = Agent(
    name="点餐员",
    instructions="""你是麦当劳的点餐员。
    1. 负责记录顾客想吃的餐品。
    2. 如果顾客要点薯条，立刻调用 transfer_to_fries 交接给炸薯条师傅。
    3. 如果顾客要点炸鸡/麦乐鸡，立刻调用 transfer_to_chicken 交接给炸鸡师傅。
    4. 如果顾客要点可乐/饮料，立刻调用 transfer_to_cola 交接给倒可乐专员。
    5. 记住，你只管记录和转接，不要自己去后厨制作食物。""",
    functions=[transfer_to_fries, transfer_to_chicken, transfer_to_cola]
)