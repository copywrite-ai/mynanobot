from typing import Any
from .base import BaseTool
from ..cron import CronService, CronSchedule

class CronTool(BaseTool):
    """用于管理定时提醒和周期性任务的工具。"""
    
    def __init__(self, cron_service: CronService):
        self._cron = cron_service
        self._channel = "feishu" # 默认通道
        self._sender = ""

    def set_context(self, sender: str, channel: str = "feishu"):
        """设置当前会话上下文，以便定时任务触发时知道发给谁。"""
        self._sender = sender
        self._channel = channel

    @property
    def name(self) -> str:
        return "cron"

    @property
    def description(self) -> str:
        return "管理定时提醒和周期性任务。支持动作：add (添加), list (查看), remove (删除)。"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "remove"],
                    "description": "要执行的动作"
                },
                "message": {"type": "string", "description": "提醒内容（用于 add）"},
                "every_seconds": {"type": "integer", "description": "间隔秒数（用于周期任务）"},
                "cron_expr": {"type": "string", "description": "Cron 表达式，如 '0 9 * * *'"},
                "at": {"type": "string", "description": "ISO 时间格式，如 '2026-03-04T12:00:00'（用于一次性提醒）"},
                "job_id": {"type": "string", "description": "任务 ID（用于 remove）"}
            },
            "required": ["action"]
        }

    async def execute(self, action: str, **kwargs: Any) -> str:
        if action == "add":
            return self._add_job(**kwargs)
        elif action == "list":
            return self._list_jobs()
        elif action == "remove":
            return self._remove_job(kwargs.get("job_id"))
        return f"未知动作: {action}"

    def _add_job(self, message: str = "", every_seconds: int = None, 
                 cron_expr: str = None, at: str = None, **kwargs) -> str:
        if not message:
            return "错误：添加任务必须提供提醒内容 (message)。"
        if not self._sender:
            return "错误：无法获取当前会话上下文 (sender)。"

        # 构建调度
        if every_seconds:
            schedule = CronSchedule(kind="every", every_ms=every_seconds * 1000)
            delete_after = False
        elif cron_expr:
            schedule = CronSchedule(kind="cron", expr=cron_expr)
            delete_after = False
        elif at:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(at)
                at_ms = int(dt.timestamp() * 1000)
                schedule = CronSchedule(kind="at", at_ms=at_ms)
                delete_after = True
            except ValueError:
                return f"错误：时间格式无效 '{at}'，请使用 ISO 格式。"
        else:
            return "错误：必须提供 every_seconds, cron_expr 或 at 其中之一。"

        job = self._cron.add_job(
            name=message[:20] + "...",
            schedule=schedule,
            message=message,
            deliver=True,
            channel=self._channel,
            to=self._sender,
            delete_after_run=delete_after
        )
        return f"成功创建任务 '{job.name}' (ID: {job.id})"

    def _list_jobs(self) -> str:
        jobs = self._cron.list_jobs()
        if not jobs:
            return "当前没有定时任务。"
        
        lines = []
        for j in jobs:
            status = "启用" if j.enabled else "禁用"
            lines.append(f"- [{j.id}] {j.name} (类型: {j.schedule.kind}, 状态: {status})")
        return "当前定时任务列表：\n" + "\n".join(lines)

    def _remove_job(self, job_id: str) -> str:
        if not job_id:
            return "错误：删除任务必须提供 job_id。"
        if self._cron.remove_job(job_id):
            return f"任务 {job_id} 已成功删除。"
        return f"找到不 ID 为 {job_id} 的任务。"
