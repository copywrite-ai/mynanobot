import os
import asyncio

# 配置信息 (请在启动容器时通过环境变量注入)
APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

async def start_dummy_bot():
    print("This is a cleaned placeholder for lab6.")
    print(f"Current APP_ID config: {APP_ID[:6]}***")

if __name__ == "__main__":
    asyncio.run(start_dummy_bot())
