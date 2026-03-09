import asyncio
import os
from dotenv import load_dotenv
from nanocore.logger import logger

# 加载 .env 环境变量
load_dotenv()
from nanocore.bus import MessageBus
from nanocore.agent import AgentBrain
from nanocore.connectors.feishu import FeishuConnector
from nanocore.connectors.slack import SlackConnector
from nanocore.tools.media import MediaTool

# 配置信息 (从环境变量读取)
APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
LM_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
LM_MODEL = os.getenv("LM_MODEL", "local-model")
LM_API_KEY = os.getenv("LM_API_KEY", "lm-studio")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
BOT_LANGUAGE = os.getenv("BOT_LANGUAGE", "zh")

# 语言包 (Localization)
STRINGS = {
    "zh": {
        "feishu_missing": "⚠️ [Feishu] 未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET，飞书通道未启动。",
        "slack_missing": "⚠️ [Slack] 未配置 SLACK_BOT_TOKEN 或 SLACK_APP_TOKEN，Slack 通道未启动。",
        "starting": "✨ [mynanocloud] 极简框架版启动中...",
        "shutdown": "\n👋 机器人已安全关闭。",
        "cron_pushing": "📡 [Cron] 正在推送提醒到通道 {channel} -> {to}",
        "cron_empty": "⚠️ [Cron] 任务 {job_id} 处理完毕，但 AI 返回内容为空，未推送。",
        "cron_prompt_prefix": "SYSTEM: 定时提醒到期。",
        "cron_prompt_time": "触发时间:",
        "cron_prompt_content": "提醒内容:",
        "cron_prompt_guide": "重要指引：\n1. 如果‘提醒内容’是一个简单的文本信息，请直接回复内容。\n2. 如果内容明确要求执行指令，请调用工具并汇报结果。"
    },
    "en": {
        "feishu_missing": "⚠️ [Feishu] FEISHU_APP_ID or FEISHU_APP_SECRET not configured. Feishu connector skipped.",
        "slack_missing": "⚠️ [Slack] SLACK_BOT_TOKEN or SLACK_APP_TOKEN not configured. Slack connector skipped.",
        "starting": "✨ [mynanocloud] Minimal framework starting...",
        "shutdown": "\n👋 Bot has been safely shut down.",
        "cron_pushing": "📡 [Cron] Pushing reminder to channel {channel} -> {to}",
        "cron_empty": "⚠️ [Cron] Job {job_id} finished, but AI returned empty content. Not pushed.",
        "cron_prompt_prefix": "SYSTEM: Scheduled reminder triggered.",
        "cron_prompt_time": "Trigger Time:",
        "cron_prompt_content": "Content:",
        "cron_prompt_guide": "GUIDELINES:\n1. If the content is simple text, just reply with it.\n2. If it asks for an action, call the tool and report the result."
    }
}
s = STRINGS.get(BOT_LANGUAGE, STRINGS["en"])

from nanocore.tools.base import ToolRegistry
from nanocore.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool, EditFileTool
from nanocore.tools.shell import ExecTool
from nanocore.session import SessionManager
from nanocore.tools.memory import MemoryStore, SaveMemoryTool
from nanocore.cron import CronService
from nanocore.tools.cron import CronTool
from nanocore.tools.clock import ClockTool
from nanocore.subagent import SubagentManager
from nanocore.tools.spawn import SpawnTool
from pathlib import Path


async def start_my_bot():
    # 1. 初始化总线和持久化层
    bus = MessageBus()
    session_manager = SessionManager(Path("data/sessions"))
    memory_store = MemoryStore()

    # 2. 初始化工具注册表并注册工具
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirTool())
    registry.register(EditFileTool())
    registry.register(ExecTool())
    registry.register(MediaTool()) # 注册媒体控制工具
    registry.register(SaveMemoryTool(memory_store)) # 注册记忆工具
    
    # 3. 初始化定时任务服务
    cron_store_path = Path("data/cron/jobs.json")
    cron_service = CronService(cron_store_path)

    # 4. 初始化子代理管理器 (SubagentManager)
    lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    
    def brain_factory():
        """为子代理创建专用的大脑实例。"""
        sub_registry = ToolRegistry()
        sub_registry.register(ReadFileTool())
        sub_registry.register(WriteFileTool())
        sub_registry.register(ListDirTool())
        sub_registry.register(EditFileTool())
        sub_registry.register(ExecTool())
        sub_registry.register(MediaTool())
        sub_registry.register(SaveMemoryTool(memory_store))
        
        return AgentBrain(bus, model=LM_MODEL, base_url=LM_URL, api_key=LM_API_KEY,
                          tool_registry=sub_registry, 
                          session_manager=None, memory_store=memory_store)

    subagent_manager = SubagentManager(brain_factory, bus)
    registry.register(SpawnTool(subagent_manager)) # 注册分身工具

    # 5. 初始化大脑
    brain = AgentBrain(bus, model=LM_MODEL, base_url=LM_URL, api_key=LM_API_KEY,
                       tool_registry=registry, 
                       session_manager=session_manager, memory_store=memory_store,
                       subagent_manager=subagent_manager)

    # 定义定时任务回调
    async def on_cron_job(job):
        # 获取实际执行时间
        from datetime import datetime
        trigger_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 使用更明确的指令，区分“内容推送”和“指令执行”
        trigger_prompt = (
            f"{s['cron_prompt_prefix']}\n"
            f"{s['cron_prompt_time']} {trigger_time}\n"
            f"{s['cron_prompt_content']} {job.payload.message}\n"
            f"---\n"
            f"{s['cron_prompt_guide']}"
        )
        
        # 建议使用独立的 session_id (如 cron:job_id)，避免与用户的日常对话背景混淆
        cron_session_id = f"cron:{job.id}"
        
        response_text = await brain.process_direct(trigger_prompt, sender=cron_session_id)
        
        if job.payload.deliver and job.payload.to:
            logger.info(s["cron_pushing"].format(channel=job.payload.channel, to=job.payload.to))
            # 在消息前加上时间戳
            final_message = f"⏰ {trigger_time}\n{response_text}"
            await bus.outbound.put({
                "sender": job.payload.to,
                "text": final_message,
                "status": "finished"
            })
        elif job.payload.deliver and not response_text:
            logger.warning(s["cron_empty"].format(job_id=job.id))
    
    cron_service.on_job = on_cron_job
    registry.register(CronTool(cron_service)) # 注册定时工具
    registry.register(ClockTool()) # 注册时钟工具

    # 5. 初始化通道并启动
    tasks = [brain.run(), cron_service.start()]

    if APP_ID and APP_SECRET:
        feishu = FeishuConnector(bus, APP_ID, APP_SECRET)
        tasks.extend([feishu.watch_outbound(), feishu.start()])
    else:
        logger.warning(s["feishu_missing"])

    if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
        slack = SlackConnector(bus, SLACK_BOT_TOKEN, SLACK_APP_TOKEN)
        tasks.extend([slack.watch_outbound(), slack.start()])
    else:
        logger.warning(s["slack_missing"])
    
    logger.info(s["starting"])
    
    # 7. 并发运行所有组件
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(start_my_bot())
    except KeyboardInterrupt:
        print(s["shutdown"])
