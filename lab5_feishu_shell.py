import asyncio
import json
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

console = Console()

# 1. 模拟飞书的“黑话” (JSON 数据包)
# 真实的 nanobot 也会收到类似这样的 JSON
MOCK_FEISHU_EVENT = {
    "header": {
        "event_id": "abcd-1234",
        "event_type": "im.message.receive_v1"
    },
    "event": {
        "sender": {
            "sender_id": {"open_id": "ou_12345"},
            "sender_type": "user"
        },
        "message": {
            "content": "{\"text\":\"你好啊，Bot，帮我写一段 Python 代码吧\"}",
            "msg_type": "text"
        }
    }
}

# 2. 模拟消息总线
class MessageBus:
    def __init__(self):
        self.inbound = asyncio.Queue()
        self.outbound = asyncio.Queue()

# 3. 飞书连接器 (Feishu Connector)
# 它的工作是：翻译官 + 搬运工
class FeishuConnector:
    def __init__(self, bus: MessageBus):
        self.bus = bus

    async def simulate_receive(self, event_json):
        """将飞书的 JSON 翻译成 Bot 可理解的消息"""
        event_data = event_json.get("event", {})
        msg_content = json.loads(event_data.get("message", {}).get("content", "{}"))
        text = msg_content.get("text", "")
        sender = event_data.get("sender", {}).get("sender_id", {}).get("open_id", "未知用户")
        
        console.print(f"\n[bold cyan]📱 飞书外壳[/bold cyan]: 收到来自 [yellow]{sender}[/yellow] 的原始事件...")
        
        # 放入总线
        await self.bus.inbound.put({"sender": sender, "text": text})

    async def watch_outbound(self):
        """盯着总线，把回信包装成飞书格式发出去"""
        while True:
            msg = await self.bus.outbound.get()
            # 模拟飞书发送格式
            feishu_payload = {
                "receive_id": msg["sender"],
                "msg_type": "text",
                "content": json.dumps({"text": msg["text"]})
            }
            console.print(Panel(
                Text(f"发送给飞书: {feishu_payload.get('content')}", style="green"),
                title="📤 飞书外壳 -> 飞书 API",
                border_style="cyan"
            ))

# 4. 简化的 AI 大脑
async def agent_brain(bus: MessageBus):
    while True:
        incoming = await bus.inbound.get()
        print(f"🧠 大脑：正在思考如何回复 {incoming['text']}...")
        await asyncio.sleep(1.5)
        
        reply = f"你好 {incoming['sender']}！我已经收到了你的请求：'{incoming['text']}'。这是我的回复：[Python 代码示例...]"
        await bus.outbound.put({"sender": incoming["sender"], "text": reply})

# 5. 主程序：演示连接过程
async def main():
    bus = MessageBus()
    feishu = FeishuConnector(bus)
    
    console.print(Panel.fit(
        "🚀 [bold]飞书外壳实验室 (Feishu Shell Lab)[/bold]\n展示消息是如何从飞书传递给 AI 的",
        padding=(1, 2)
    ))

    # 启动异步任务
    tasks = [
        asyncio.create_task(agent_brain(bus)),
        asyncio.create_task(feishu.watch_outbound())
    ]
    
    # 模拟一次事件触发
    await asyncio.sleep(1)
    await feishu.simulate_receive(MOCK_FEISHU_EVENT)
    
    # 给点时间看效果
    await asyncio.sleep(5)
    for t in tasks:
        t.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
