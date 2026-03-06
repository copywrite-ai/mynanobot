import asyncio
import json
import time
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal, Any, Callable, Coroutine
from datetime import datetime
from .logger import logger

@dataclass
class CronSchedule:
    kind: Literal["at", "every", "cron"]
    at_ms: int | None = None
    every_ms: int | None = None
    expr: str | None = None
    tz: str | None = None

@dataclass
class CronPayload:
    kind: Literal["system_event", "agent_turn"] = "agent_turn"
    message: str = ""
    deliver: bool = False
    channel: str | None = None
    to: str | None = None

@dataclass
class CronJobState:
    next_run_at_ms: int | None = None
    last_run_at_ms: int | None = None
    last_status: str | None = None
    last_error: str | None = None

@dataclass
class CronJob:
    id: str
    name: str
    enabled: bool = True
    schedule: CronSchedule = field(default_factory=lambda: CronSchedule(kind="every"))
    payload: CronPayload = field(default_factory=CronPayload)
    state: CronJobState = field(default_factory=CronJobState)
    created_at_ms: int = 0
    updated_at_ms: int = 0
    delete_after_run: bool = False

def _now_ms() -> int:
    return int(time.time() * 1000)

def _compute_next_run(schedule: CronSchedule, now_ms: int) -> int | None:
    if schedule.kind == "at":
        if schedule.at_ms:
            if schedule.at_ms > now_ms:
                return schedule.at_ms  # 未来时间，正常调度
            else:
                return now_ms  # 时间已过去，返回当前时间，立即执行
        return None
    if schedule.kind == "every":
        interval = schedule.every_ms or 0
        if interval <= 0:
            return None
        
        # 优化：如果间隔是整秒或整分钟，对齐到时钟刻度
        # 例如：every 5m，不论现在是 14:02:30，下一次都瞄准 14:05:00
        if interval >= 1000 and interval % 1000 == 0:
            # 对齐到 Unix Epoch 以来的整数倍
            return ((now_ms // interval) + 1) * interval
            
        return now_ms + interval
    if schedule.kind == "cron" and schedule.expr:
        try:
            from croniter import croniter
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(schedule.tz) if schedule.tz else None
            base_dt = datetime.fromtimestamp(now_ms / 1000, tz=tz)
            it = croniter(schedule.expr, base_dt)
            return int(it.get_next(datetime).timestamp() * 1000)
        except Exception:
            return None
    return None

def _compute_next_after_due(schedule: CronSchedule, due_ms: int, now_ms: int) -> int | None:
    """基于“原定触发时间”计算下一次，并跳过已经错过的周期，防止连环补触发。"""
    if schedule.kind == "every":
        interval = schedule.every_ms or 0
        if interval <= 0:
            return None
        nxt = due_ms + interval
        while nxt <= now_ms:
            nxt += interval
        return nxt
    if schedule.kind == "cron":
        nxt = _compute_next_run(schedule, due_ms)
        while nxt is not None and nxt <= now_ms:
            nxt = _compute_next_run(schedule, nxt)
        return nxt
    return None

class CronService:
    def __init__(self, store_path: Path, on_job: Callable[[CronJob], Coroutine[Any, Any, str | None]] = None):
        self.store_path = Path(store_path)
        self.on_job = on_job
        self.jobs: list[CronJob] = []
        self._timer_task: asyncio.Task | None = None
        self._job_tasks: dict[str, asyncio.Task] = {}
        self._running = False
        self._load()

    def _load(self):
        if not self.store_path.exists():
            return
        try:
            data = json.loads(self.store_path.read_text())
            for j in data.get("jobs", []):
                job = CronJob(
                    id=j["id"], name=j["name"], enabled=j.get("enabled", True),
                    schedule=CronSchedule(**j["schedule"]),
                    payload=CronPayload(**j["payload"]),
                    state=CronJobState(**j.get("state", {})),
                    created_at_ms=j.get("created_at_ms", 0),
                    updated_at_ms=j.get("updated_at_ms", 0),
                    delete_after_run=j.get("delete_after_run", False)
                )
                self.jobs.append(job)
        except Exception as e:
            logger.error(f"⚠️ [Cron] 加载失败: {e}")

    def _save(self):
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"jobs": []}
        for j in self.jobs:
            data["jobs"].append({
                "id": j.id, "name": j.name, "enabled": j.enabled,
                "schedule": vars(j.schedule),
                "payload": vars(j.payload),
                "state": vars(j.state),
                "created_at_ms": j.created_at_ms,
                "updated_at_ms": j.updated_at_ms,
                "delete_after_run": j.delete_after_run
            })
        self.store_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    async def start(self):
        self._running = True
        self._recompute_next_runs()
        self._arm_timer()
        logger.info(f"⏰ [Cron] 服务已启动，包含 {len(self.jobs)} 个任务。")

    def stop(self):
        self._running = False
        if self._timer_task:
            self._timer_task.cancel()
        for task in self._job_tasks.values():
            task.cancel()
        self._job_tasks.clear()

    def _recompute_next_runs(self):
        now = _now_ms()
        for job in self.jobs:
            if job.enabled and not job.state.next_run_at_ms:
                job.state.next_run_at_ms = _compute_next_run(job.schedule, now)

    def _arm_timer(self):
        if self._timer_task:
            self._timer_task.cancel()
        
        times = [j.state.next_run_at_ms for j in self.jobs if j.enabled and j.state.next_run_at_ms]
        if not times or not self._running:
            return
        
        next_wake = min(times)
        delay = max(0, (next_wake - _now_ms()) / 1000)

        async def _tick():
            await asyncio.sleep(delay)
            if self._running:
                await self._on_timer()
        
        self._timer_task = asyncio.create_task(_tick())

    async def _on_timer(self):
        now = _now_ms()
        due = [j for j in self.jobs if j.enabled and j.state.next_run_at_ms and now >= j.state.next_run_at_ms]
        
        for job in due:
            self._dispatch_job(job, now)
        
        self._save()
        self._arm_timer()

    def _dispatch_job(self, job: CronJob, now_ms: int):
        due_ms = job.state.next_run_at_ms or now_ms

        # 先推进下一次触发时间，避免执行耗时拖慢节拍
        if job.schedule.kind == "at":
            job.state.next_run_at_ms = None
        else:
            job.state.next_run_at_ms = _compute_next_after_due(job.schedule, due_ms, now_ms)

        running_task = self._job_tasks.get(job.id)
        if running_task and not running_task.done():
            logger.warning(f"⏭️ [Cron] 任务仍在执行，跳过本次重入: {job.name} ({job.id})")
            return

        task = asyncio.create_task(self._execute_job(job))
        self._job_tasks[job.id] = task

    async def _execute_job(self, job: CronJob):
        logger.info(f"⚡️ [Cron] 正在触发任务: {job.name} ({job.id})")
        start_ms = _now_ms()
        
        # 添加执行时间戳到 job 对象
        job.triggered_at_ms = start_ms
        
        try:
            if self.on_job:
                await self.on_job(job)
            job.state.last_status = "ok"
            job.state.last_error = None
        except Exception as e:
            job.state.last_status = "error"
            job.state.last_error = str(e)
            logger.error(f"❌ [Cron] 任务执行失败: {e}")
        
        job.state.last_run_at_ms = start_ms
        job.updated_at_ms = _now_ms()

        if job.schedule.kind == "at":
            if job.delete_after_run:
                self.jobs = [j for j in self.jobs if j.id != job.id]
                self._job_tasks.pop(job.id, None) # 彻底清理追踪
            else:
                job.enabled = False
                job.state.next_run_at_ms = None
        self._save()

    def add_job(self, name: str, schedule: CronSchedule, message: str, 
                deliver=False, channel=None, to=None, delete_after_run=False) -> CronJob:
        now = _now_ms()
        job = CronJob(
            id=str(uuid.uuid4())[:8], name=name, enabled=True,
            schedule=schedule,
            payload=CronPayload(message=message, deliver=deliver, channel=channel, to=to),
            state=CronJobState(next_run_at_ms=_compute_next_run(schedule, now)),
            created_at_ms=now, updated_at_ms=now, delete_after_run=delete_after_run
        )
        self.jobs.append(job)
        self._save()
        self._arm_timer()
        return job

    def list_jobs(self) -> list[CronJob]:
        return self.jobs

    async def run_job(self, job_id: str) -> bool:
        for job in self.jobs:
            if job.id == job_id:
                self._dispatch_job(job, _now_ms())
                return True
        return False

    def remove_job(self, job_id: str) -> bool:
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j.id != job_id]
        if len(self.jobs) < before:
            # 停止并移除正在运行的任务
            task = self._job_tasks.pop(job_id, None)
            if task and not task.done():
                task.cancel()
                logger.info(f"🚫 [Cron] 已强行停止并移除任务: {job_id}")
            
            self._save()
            self._arm_timer()
            return True
        return False

    def clear_jobs(self) -> int:
        count = len(self.jobs)
        # 停止所有正在运行的任务
        for job_id, task in self._job_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"🚫 [Cron] 已取消正在运行的任务: {job_id}")
        self._job_tasks.clear()
        
        self.jobs = []
        self._save()
        self._arm_timer()
        logger.info(f"🧹 [Cron] 已清空所有任务 (共 {count} 个)")
        return count
