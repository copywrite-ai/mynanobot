import asyncio

class MessageBus:
    """模仿 nanobot 的核心消息总线，负责组件间解耦。"""
    def __init__(self):
        self.inbound = asyncio.Queue()  # 进站消息（由 Connector 填充）
        self.outbound = asyncio.Queue() # 出站消息（由 Agent 填充）

if __name__ == "__main__":
    # 简单的本地测试：看看总线能不能传东西
    async def test_bus():
        bus = MessageBus()
        await bus.inbound.put({"sender": "test_user", "text": "Hello Bus!"})
        msg = await bus.inbound.get()
        print(f"📦 总线测试成功！收到消息: {msg['text']}")

    asyncio.run(test_bus())
