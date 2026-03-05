import asyncio
import uuid
import json
from .logger import logger

class SubagentManager:
    """管理后台子代理的运行和生命周期。"""

    def __init__(self, brain_factory, bus):
        """
        Args:
            brain_factory: 一个函数，调用它能产生一个带有基础配置的 AgentBrain 实例
            bus: 消息总线
        """
        self.brain_factory = brain_factory
        self.bus = bus
        self._running_tasks = {} # task_id -> asyncio.Task

    async def spawn(self, task: str, label: str = None, sender: str = "main_agent"):
        """启动一个后台子代理去完成特定任务。"""
        task_id = str(uuid.uuid4())[:8]
        display_label = label or (task[:30] + "...")
        
        # 启动异步任务
        bg_task = asyncio.create_task(
            self._run_subagent(task_id, task, display_label, sender)
        )
        self._running_tasks[task_id] = bg_task
        
        # 任务结束后的清理
        bg_task.add_done_callback(lambda t: self._running_tasks.pop(task_id, None))
        
        logger.info(f"🚀 [SubagentManager] 已启动子代理 [{task_id}]: {display_label}")
        return f"子代理已启动 (ID: {task_id})。任务完成后我会通过系统消息通知你。"

    async def _run_subagent(self, task_id: str, task: str, label: str, sender: str):
        """子代理的具体运行逻辑。"""
        logger.info(f"⏳ [Subagent] 子代理 {task_id} 开始执行: {label}")
        
        try:
            # 1. 创建一个新的大脑实例用于子代理
            # 注意：子代理通常不需要 session_manager，因为它是单轮任务
            brain = self.brain_factory()
            
            # 2. 构建子代理的指令环境
            prompt = (
                f"SYSTEM: 你是一个子代理（Subagent），负责完成主代理交给你的特定子任务。\n"
                f"当前任务: {task}\n"
                f"请直接执行该任务，并在完成后给出最终总结。请勿尝试与用户聊天。"
            )
            
            # 3. 直接调用大脑的 process_direct 处理
            # 使用特殊的 session_id 以隔离记忆
            sub_session_id = f"subagent:{task_id}"
            result = await brain.process_direct(prompt, sender=sub_session_id)
            
            # 4. 将结果作为系统消息回传到总线
            report = (
                f"【子代理汇报 - {label}】\n\n"
                f"任务目标: {task}\n"
                f"执行结果: {result}\n\n"
                f"请根据此结果继续你的主线任务。"
            )
            
            await self.bus.inbound.put({
                "sender": "system",
                "text": report,
                "chat_id": sender # 回传到当初触发的聊天窗口
            })
            
            logger.info(f"✅ [Subagent] 子代理 {task_id} 顺利完成。")
            
        except asyncio.CancelledError:
            logger.warning(f"🛑 [Subagent] 子代理 {task_id} 被强制中断。")
        except Exception as e:
            logger.error(f"❌ [Subagent] 子代理 {task_id} 执行出错: {e}")
            await self.bus.inbound.put({
                "sender": "system",
                "text": f"【子代理报错 - {label}】执行过程中遇到错误: {e}",
                "chat_id": sender
            })

    async def stop_all(self):
        """停止所有运行中的子代理。"""
        count = len(self._running_tasks)
        for task_id, task in self._running_tasks.items():
            task.cancel()
        
        if count > 0:
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
            logger.info(f"⏹ [SubagentManager] 已停止 {count} 个运行中的任务。")
        return count
