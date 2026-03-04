import asyncio

# 1. 模拟 nanobot 的 MessageBus (消息总线)
# 想象这是一个邮局，有两个邮筒：一个收件，一个寄件。
class SimpleBus:
    def __init__(self):
        self.inbound = asyncio.Queue()  # 进站消息（用户 -> 大脑）
        self.outbound = asyncio.Queue() # 出站消息（大脑 -> 用户）

# 2. 模拟“大脑任务” (Agent Worker)
# 它就在邮局里守着，看到有信进来就读，读完写回信放进寄件筒。
async def agent_brain(bus: SimpleBus):
    print("🧠 大脑任务：已就绪，正在等待消息...")
    while True:
        # 从“进站”邮筒拿信 (如果没信，它会在这里休息等待)
        message = await bus.inbound.get()
        print(f"🧠 大脑任务：收到新信件 —— '{message}'")
        
        # 思考一下（模拟延迟）
        await asyncio.sleep(1)
        
        # 写回信并放进“出站”邮筒
        reply = f"这是对 '{message}' 的回复"
        await bus.outbound.put(reply)
        print(f"🧠 大脑任务：回信已放入寄件筒。")

# 3. 模拟“飞书/Telegram 任务” (Channel Worker)
# 它负责把信从外面送进邮局，并把回信拿给外面的用户。
async def feishu_channel(bus: SimpleBus):
    print("📱 飞书通道：已连接。")
    
    # 模拟用户在飞书发了一条消息
    await asyncio.sleep(2)
    print("\n👤 用户在飞书说：'你好，Bot！'")
    await bus.inbound.put("你好，Bot！")

    # 盯着“出站”邮筒，看到有回信就发给用户
    while True:
        reply = await bus.outbound.get()
        print(f"📱 飞书通道：已送达回信 —— '{reply}'")
        print("✅ 任务完成！")
        break # 演示完一次就结束

# 4. 启动“多任务并发” (模仿 nanobot/cli/commands.py 第 584 行)
async def main():
    bus = SimpleBus()
    
    # 同时启动大脑和通道（就像 nanobot 同时启动多个平台接口一样）
    # asyncio.gather 就像是让好几个人同时开始工作
    await asyncio.gather(
        agent_brain(bus),
        feishu_channel(bus)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已停止。")
