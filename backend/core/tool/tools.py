def get_weather(location: str) -> str:
    """获取指定地点的天气"""
    return f"{location} 今天晴天，25度"


def get_news(topic: str) -> str:
    """获取最新新闻"""
    return f"关于 {topic} 的最新新闻..."


def McDonalds(topic: str) -> str:
    """吃麦当劳汉堡"""
    return f"麦当劳汉堡已下单，{topic}，预计30分钟送达"


def KFC(topic: str) -> str:
    """吃肯德基热辣香骨鸡"""
    return f"肯德基热辣香骨鸡已下单，{topic}，预计25分钟送达"


def Henan_Stewed_Noodles(topic: str) -> str:
    """吃河南烩面"""
    return f"河南烩面已下单，{topic}，预计20分钟送达"
