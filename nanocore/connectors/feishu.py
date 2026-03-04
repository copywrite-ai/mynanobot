import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    P2ImMessageReceiveV1, 
    CreateMessageRequest, 
    CreateMessageRequestBody,
    CreateMessageReactionRequest, 
    CreateMessageReactionRequestBody, 
    Emoji
)

class FeishuConnector:
    """模仿 nanobot 的飞书通道。"""
    def __init__(self, bus, app_id, app_secret):
        self.bus = bus
        self.app_id = app_id
        self.app_secret = app_secret
        self.client = None
        self.loop = None
        self._executor = ThreadPoolExecutor(max_workers=10) # 专用线程池
        self._running = False

    async def start(self):
        self.loop = asyncio.get_running_loop()
        self.client = lark.Client.builder().app_id(self.app_id).app_secret(self.app_secret).build()
        self._running = True
        
        handler = lark.EventDispatcherHandler.builder("", "") \
            .register_p2_im_message_receive_v1(self._on_message_sync) \
            .build()
        
        ws_client = lark.ws.Client(self.app_id, self.app_secret, event_handler=handler)
        
        # 将 WS client 放在独立的后台线程运行，不占用 loop 的默认 executor
        def run_ws():
            print("🚀 [nanocore] 飞书连接已启动。")
            while self._running:
                try:
                    ws_client.start()
                except Exception as e:
                    print(f"⚠️ [飞书] WebSocket 异常断开: {e}")
                    import time
                    time.sleep(5) # 失败重试

        threading.Thread(target=run_ws, daemon=True).start()

    def _on_message_sync(self, data: P2ImMessageReceiveV1) -> None:
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._on_message(data), self.loop)

    async def _on_message(self, data: P2ImMessageReceiveV1):
        event = data.event
        sender_id = event.sender.sender_id.open_id
        message_id = event.message.message_id
        content_json = json.loads(event.message.content)
        text = content_json.get("text", "")
        
        print(f"📥 [飞书] 收到消息: '{text}' (ID: {message_id})")
        
        # 立即给一个确认 (Confirm Receive)
        await self._send_reaction(message_id, "THUMBSUP")
        
        await self.bus.inbound.put({
            "sender": sender_id, 
            "text": text, 
            "message_id": message_id
        })

    async def _send_reaction(self, message_id: str, emoji_type: str):
        """发送表情回复"""
        print(f"⚡️ [飞书] 尝试打表情: {emoji_type} 到消息 {message_id}")
        try:
            from lark_oapi.api.im.v1 import CreateMessageReactionRequest, CreateMessageReactionRequestBody, Emoji
            request = CreateMessageReactionRequest.builder() \
                .message_id(message_id) \
                .request_body(
                    CreateMessageReactionRequestBody.builder()
                    .reaction_type(Emoji.builder().emoji_type(emoji_type).build())
                    .build()
                ).build()
            
            response = await self.loop.run_in_executor(self._executor, self.client.im.v1.message_reaction.create, request)
            if not response.success():
                print(f"❌ [飞书] 发送表情 {emoji_type} 失败: {response.code} - {response.msg}")
            else:
                print(f"✅ [飞书] 表情 {emoji_type} 发送成功")
        except Exception as e:
            print(f"⚠️ [飞书] 发送表情 {emoji_type} 触发异常: {e}")

    async def watch_outbound(self):
        while True:
            msg = await self.bus.outbound.get()
            receive_id = msg["sender"]
            message_id = msg.get("message_id")
            status = msg.get("status")
            text = msg.get("text", "")

            # 处理状态反应
            if message_id:
                if status == "processing":
                    # 正在处理
                    await self._send_reaction(message_id, "Typing")
                elif status in ["finished", "error"]:
                    # 完成
                    await self._send_reaction(message_id, "Done")

            # 只有在 finished 或 error 或 显式传了 text 时才发送卡片
            if text:
                request = CreateMessageRequest.builder() \
                    .receive_id_type("open_id") \
                    .request_body(
                        CreateMessageRequestBody.builder()
                        .receive_id(receive_id)
                        .msg_type("text")
                        .content(json.dumps({"text": text}))
                        .build()
                    ).build()
                
                await self.loop.run_in_executor(self._executor, self.client.im.v1.message.create, request)

if __name__ == "__main__":
    # 独立测试飞书通道：只测试连接，不连 AI 大脑
    async def test_feishu():
        from nanocore.bus import MessageBus
        bus = MessageBus()
        
        # 请在环境变量中设置真实 APP_ID 和 SECRET 进行测试
        APP_ID = os.getenv("FEISHU_APP_ID", "")
        APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
        
        feishu = FeishuConnector(bus, APP_ID, APP_SECRET)
        
        # 启动监听和发送
        async def watch():
            while True:
                msg = await bus.inbound.get()
                print(f"📥 [飞书接收测试] 收到消息: {msg['text']}")
                await bus.outbound.put({"sender": msg["sender"], "text": f"收到！你说的是: {msg['text']}"})

        await asyncio.gather(feishu.start(), feishu.watch_outbound(), watch())

    asyncio.run(test_feishu())
