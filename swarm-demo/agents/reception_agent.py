from core.agent import Agent
from agents.order_agent import order_agent

def transfer_to_order():
    """交接函数：当顾客明确表示要点餐、看菜单时，交接给点餐员"""
    return order_agent

reception_agent = Agent(
    name="迎宾员",
    instructions="""你是麦当劳的迎宾员。
    1. 负责热情地欢迎顾客。
    2. 解答营业时间（早8点到晚10点）、洗手间位置等基础问题。
    3. 如果顾客要点餐，立刻调用 transfer_to_order 交接给点餐员。不要自己尝试帮他点餐。""",
    functions=[transfer_to_order]
)