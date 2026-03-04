from pathlib import Path
from .base import BaseTool

class MemoryStore:
    """持久化长期记忆（Markdown 文件）。"""
    def __init__(self, memory_file: str = "MEMORY.md"):
        self.memory_file = Path(memory_file)

    def read(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write(self, content: str):
        self.memory_file.write_text(content, encoding="utf-8")

class SaveMemoryTool(BaseTool):
    name = "save_memory"
    description = "将重要的事实或偏好保存到长期记忆中。"
    parameters = {
        "type": "object",
        "properties": {
            "memory_update": {
                "type": "string", 
                "description": "要更新的完整 Markdown 格式长期记忆内容。包含之前的所有重要事实并加入新事实。"
            }
        },
        "required": ["memory_update"]
    }

    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    async def execute(self, memory_update: str) -> str:
        try:
            self.memory_store.write(memory_update)
            return "✅ 长期记忆已成功更新。"
        except Exception as e:
            return f"❌ 更新长期记忆失败: {str(e)}"
