import asyncio
import os
from nanocore.logger import logger
from nanocore.bus import MessageBus
from nanocore.agent import AgentBrain
from nanocore.connectors.feishu import FeishuConnector

# 配置信息 (从环境变量读取)
APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

from nanocore.tools.base import ToolRegistry
from nanocore.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool, EditFileTool
from nanocore.tools.shell import ExecTool
from nanocore.session import SessionManager
from nanocore.tools.memory import MemoryStore, SaveMemoryTool
from nanocore.cron import CronService
from nanocore.tools.cron import CronTool
from pathlib import Path

# 配置信息
APP_ID = "cli_a92f341516f85cd6"
APP_SECRET = "UeqcAN0CYicRqNRFUThfPeOQaKH4firz"

async def start_my_bot():
    # 1. 初始化总线和持久化层
    bus = MessageBus()
    session_manager = SessionManager()
    memory_store = MemoryStore()

    # 2. 初始化工具注册表并注册工具
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirTool())
    registry.register(EditFileTool())
    registry.register(ExecTool())
    registry.register(SaveMemoryTool(memory_store)) # 注册记忆工具
    
    # 3. 初始化定时任务服务
    cron_store_path = Path("data/cron/jobs.json")
    cron_service = CronService(cron_store_path)

    # 4. 初始化大脑
    lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    brain = AgentBrain(bus, base_url=lm_url, tool_registry=registry, 
                       session_manager=session_manager, memory_store=memory_store)

    # 定义定时任务回调
    async def on_cron_job(job):
        # 使用更明确的指令，告知 AI 这是定时触发，直接执行任务
        trigger_prompt = (
            f"SYSTEM: 定时任务时间已到。\n"
            f"任务: {job.name}\n"
            f"指令: {job.payload.message}\n"
            f"请执行该指令并直接汇报结果。"
        )
        
        # 建议使用独立的 session_id (如 cron:job_id)，避免与用户的日常对话背景混淆
        # 这样 AI 就不会被之前“添加任务”的对话干扰，而误以为又要添加一遍
        cron_session_id = f"cron:{job.id}"
        
        response_text = await brain.process_direct(trigger_prompt, sender=cron_session_id)
        
        if job.payload.deliver and job.payload.to:
            logger.info(f"📡 [Cron] 正在推送提醒到通道 {job.payload.channel} -> {job.payload.to}")
            await bus.outbound.put({
                "sender": job.payload.to,
                "text": response_text,
                "status": "finished"
            })
    
    cron_service.on_job = on_cron_job
    registry.register(CronTool(cron_service)) # 注册定时工具

    # 5. 初始化通道
    feishu = FeishuConnector(bus, APP_ID, APP_SECRET)
    
    logger.info("✨ [mynanocloud] 极简框架版启动中...")
    
    # 6. 并发运行所有组件
    await asyncio.gather(
        brain.run(),
        feishu.watch_outbound(),
        feishu.start(),
        cron_service.start()
    )

if __name__ == "__main__":
    try:
        asyncio.run(start_my_bot())
    except KeyboardInterrupt:
        print("\n👋 机器人已安全关闭。")
