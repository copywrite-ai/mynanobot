import asyncio
import os
from nanocore import MessageBus, AgentBrain
from nanocore.connectors.feishu import FeishuConnector

# 配置信息 (从环境变量读取)
APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

from nanocore.tools.base import ToolRegistry
from nanocore.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool, EditFileTool
from nanocore.tools.shell import ExecTool
from nanocore.session import SessionManager
from nanocore.tools.memory import MemoryStore, SaveMemoryTool

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
    
    # 3. 初始化大脑
    lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    brain = AgentBrain(bus, base_url=lm_url, tool_registry=registry, 
                       session_manager=session_manager, memory_store=memory_store)
    
    # 4. 初始化通道
    feishu = FeishuConnector(bus, APP_ID, APP_SECRET)
    
    print("✨ [mynanocloud] 极简框架版启动中...")
    
    # 4. 并发运行所有组件
    await asyncio.gather(
        brain.run(),
        feishu.watch_outbound(),
        feishu.start()
    )

if __name__ == "__main__":
    try:
        asyncio.run(start_my_bot())
    except KeyboardInterrupt:
        print("\n👋 机器人已安全关闭。")
