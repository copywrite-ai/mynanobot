import asyncio
import time

def sync_cook(name, duration):
    """
    同步煮菜：必须盯着锅，直到结束。
    """
    print(f"[同步] 开始煮: {name}")
    time.sleep(duration)
    print(f"[同步] {name} 煮好了!")

async def async_cook(name, duration):
    """
    异步煮菜：开火后可以去干别的，闹钟响了再回来。
    """
    print(f"[异步] 开始煮: {name}")
    # 这里不能用 time.sleep，因为它会卡死整个厨师。
    # 我们用 asyncio.sleep，相当于“定闹钟”。
    await asyncio.sleep(duration)
    print(f"[异步] {name} 煮好了!")

async def run_sync_demo():
    print("\n--- 开始同步模式 (一个个来) ---")
    start = time.time()
    sync_cook("炸鸡", 2)
    sync_cook("煮面", 1)
    end = time.time()
    print(f"同步总耗时: {end - start:.2f} 秒")

async def run_async_demo():
    print("\n--- 开始异步模式 (同时进行) ---")
    start = time.time()
    # 使用 gather 像指挥家一样，让两个任务同时开始
    await asyncio.gather(
        async_cook("炸鸡", 2),
        async_cook("煮面", 1)
    )
    end = time.time()
    print(f"异步总耗时: {end - start:.2f} 秒")

if __name__ == "__main__":
    # 运行演示
    asyncio.run(run_sync_demo())
    asyncio.run(run_async_demo())

    print("\n结论：异步模式下，总耗时等于最长的那个任务时间，而不是所有任务时间之和。")
