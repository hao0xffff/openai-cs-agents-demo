class Agent:
    def __init__(self, name: str, instructions: str, functions: list = None):
        self.name = name
        self.instructions = instructions
        self.functions = functions or []