import asyncio
import shlex
from typing import Any
from .base import BaseTool

class ExecTool(BaseTool):
    name = "exec"
    description = "Execute a shell command and return its output."
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "要执行的 shell 命令"}
        },
        "required": ["command"]
    }

    # 简单的黑名单 (虽然在 Docker 里运行，但还是加上基础防护)
    _DENY_LIST = ["rm -rf /", "rm -rf *", "mv /", "pkill"]

    async def execute(self, command: str) -> str:
        # 安全检查
        if any(bad in command for bad in self._DENY_LIST):
            return "错误：由于安全策略，该命令被禁止执行。"
        
        try:
            # 使用 asyncio 运行子进程
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            result = stdout.decode() + stderr.decode()
            return result or "(无输出)"
        except Exception as e:
            return f"执行命令失败: {str(e)}"
