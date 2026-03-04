import asyncio
from openai import AsyncOpenAI
import json
from pathlib import Path

# 1. 这里的配置对应之前的 lab1_onboard.py
# 假设我们要连本地的 LM Studio
# LM Studio 默认地址通常是 http://localhost:1234/v1
client = AsyncOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio" # 本地模型通常不需要真实 Key，随便填一个即可
)

async def chat_with_bot():
    """让你的 AI 助手开口说话"""
    
    print("🤖 正在连接本地 LM Studio 脑细胞...")
    
    # 模拟一个简单的消息列表（这是 Agent 的“短期记忆”）
    messages = [
        {"role": "system", "content": "你是一个幽默的初中物理老师，喜欢用生活中的例子解释科学。"},
        {"role": "user", "content": "老师，为什么天空是蓝色的？"}
    ]

    try:
        # 2. 调用 AI 大脑（这就是 nanobot/agent/loop.py 第 194 行在干的事）
        response = await client.chat.completions.create(
            model="local-model", # 这里的模型名要根据 LM Studio 加载的模型来改
            messages=messages,
            temperature=0.7,
        )

        # 3. 拿到 AI 的回答
        answer = response.choices[0].message.content
        print(f"\n👨‍🏫 老师回复：\n{answer}")

    except Exception as e:
        print(f"❌ 哎呀，连接失败了！请确认 LM Studio 已经开启了 'Local Server'。")
        print(f"错误信息: {e}")

if __name__ == "__main__":
    # 启动异步任务
    asyncio.run(chat_with_bot())
