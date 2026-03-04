import os
from pathlib import Path
from typing import Any
from .base import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "读取指定路径的文件内容。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件的绝对路径或相对路径"}
        },
        "required": ["path"]
    }

    async def execute(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            return f"错误：文件 {path} 不存在。"
        try:
            return p.read_text()
        except Exception as e:
            return f"读取文件失败: {str(e)}"

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "将内容写入指定路径的文件。如果文件不存在则创建，存在则覆盖。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目标文件路径"},
            "content": {"type": "string", "description": "要写入的文本内容"}
        },
        "required": ["path", "content"]
    }

    async def execute(self, path: str, content: str) -> str:
        p = Path(path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"✅ 文件 {path} 写入成功。"
        except Exception as e:
            return f"写入文件失败: {str(e)}"

class ListDirTool(BaseTool):
    name = "list_dir"
    description = "列出指定目录下的文件和子目录。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目录路径，默认为当前目录 '.'"}
        }
    }

    async def execute(self, path: str = ".") -> str:
        try:
            items = os.listdir(path)
            return "\n".join(items) if items else "(空目录)"
        except Exception as e:
            return f"列出目录失败: {str(e)}"

class EditFileTool(BaseTool):
    name = "edit_file"
    description = "通过替换旧文本为新文本来编辑文件。旧文本必须在文件中严格匹配且唯一。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "old_text": {"type": "string", "description": "要被替换的原始精确文本"},
            "new_text": {"type": "string", "description": "替换后的新文本"}
        },
        "required": ["path", "old_text", "new_text"]
    }

    async def execute(self, path: str, old_text: str, new_text: str) -> str:
        p = Path(path)
        if not p.exists():
            return f"错误：文件 {path} 不存在。"
        
        try:
            content = p.read_text()
            if old_text not in content:
                return f"错误：在文件 {path} 中未找到指定的旧文本。请确保 old_text 与文件内容完全一致。"
            
            count = content.count(old_text)
            if count > 1:
                return f"警告：找到 {count} 处匹配项。为了安全，请提供更具体的 old_text 以确保唯一性。"

            new_content = content.replace(old_text, new_text, 1)
            p.write_text(new_content)
            return f"✅ 文件 {path} 编辑成功。"
        except Exception as e:
            return f"编辑文件失败: {str(e)}"
