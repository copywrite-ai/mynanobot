from typing import Any

class BaseTool:
    """所有 mynanocloud 工具的基类，仿照 nanobot 设计。"""
    name: str
    description: str
    parameters: dict

    def to_openai_tool(self) -> dict:
        """生成符合 OpenAI 工具调用规范的字典。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    async def execute(self, **kwargs) -> Any:
        """具体的执行逻辑，由子类实现。"""
        raise NotImplementedError

class ToolRegistry:
    """工具注册表，负责管理和分发工具调用。"""
    def __init__(self):
        self.tools = {}

    def register(self, tool: BaseTool):
        """注册一个新工具。"""
        self.tools[tool.name] = tool

    def get_openai_tools(self) -> list[dict]:
        """获取所有已注册工具的 OpenAI Schema 列表。"""
        return [tool.to_openai_tool() for tool in self.tools.values()]

    async def call(self, name: str, args: dict) -> Any:
        """根据名称调用对应工具。"""
        if name not in self.tools:
            return f"错误：未找到名为 '{name}' 的工具。"
        
        try:
            return await self.tools[name].execute(**args)
        except Exception as e:
            return f"执行工具 '{name}' 时出错: {str(e)}"
