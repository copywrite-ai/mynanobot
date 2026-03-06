import re
from datetime import datetime, timedelta
from typing import Any
from .base import BaseTool

class ClockTool(BaseTool):
    """用于精确获取当前时间和进行时间加减计算的工具。"""

    @property
    def name(self) -> str:
        return "clock"

    @property
    def description(self) -> str:
        return "Get the current system time or calculate an ISO timestamp with an offset (e.g., '+5m', '+1h')."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["now", "delta"],
                    "description": "执行的动作：'now' (获取当前时间), 'delta' (进行时间偏移计算)"
                },
                "offset": {
                    "type": "string",
                    "description": "偏移量字符串。格式由 [+-][数字][单位] 组成。单位支持：s(秒), m(分), h(小时), d(天)。例如：'+5m' 表示 5 分钟后，'-1h' 表示 1 小时前。"
                }
            },
            "required": ["action"]
        }

    async def execute(self, action: str, offset: str = None, **kwargs: Any) -> str:
        now = datetime.now()
        
        if action == "now":
            return now.isoformat(timespec='seconds')
            
        if action == "delta":
            if not offset:
                return "错误：调用 delta 动作必须提供 offset 参数。"
            
            try:
                target_time = self._apply_offset(now, offset)
                return target_time.isoformat(timespec='seconds')
            except ValueError as e:
                return f"错误：{str(e)}"
                
        return f"未知动作: {action}"

    def _apply_offset(self, base_time: datetime, offset_str: str) -> datetime:
        """解析偏移字符串并应用到基础时间上。"""
        match = re.match(r"^([+-])(\d+)([smhd])$", offset_str.strip().lower())
        if not match:
            raise ValueError("偏移格式无效。请使用如 '+5m', '-1h' 的格式。")
            
        sign, val_str, unit = match.groups()
        val = int(val_str)
        if sign == "-":
            val = -val
            
        if unit == "s":
            delta = timedelta(seconds=val)
        elif unit == "m":
            delta = timedelta(minutes=val)
        elif unit == "h":
            delta = timedelta(hours=val)
        elif unit == "d":
            delta = timedelta(days=val)
        else:
            raise ValueError(f"不支持的单位: {unit}")
            
        return base_time + delta
