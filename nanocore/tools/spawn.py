from .base import BaseTool
from typing import Any

class SpawnTool(BaseTool):
    """用于启动后台子代理的工具。"""
    
    def __init__(self, manager):
        self._manager = manager
        self._sender = "me" # 默认发送者

    def set_context(self, sender: str):
        """设置当前会话的上下文，用于回传消息。"""
        self._sender = sender

    @property
    def name(self) -> str:
        return "spawn"

    @property
    def description(self) -> str:
        return (
            "启动一个后台子代理去完成特定任务。支持耗时较长的、可以独立运行的任务。"
            "子代理完成后会通过系统消息向你汇报结果。"
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "交给子代理执行的具体任务指令",
                },
                "label": {
                    "type": "string",
                    "description": "可选的任务简短标签（如：'分析日志'）",
                }
            },
            "required": ["task"]
        }

    async def execute(self, task: str, label: str = None, **kwargs) -> str:
        """执行派生动作。"""
        return await self._manager.spawn(task, label, sender=self._sender)
