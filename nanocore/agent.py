import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from openai import AsyncOpenAI
from .logger import logger
from .tools.base import ToolRegistry
from .session import SessionManager
from .tools.memory import MemoryStore

class AgentBrain:
    """模仿 nanobot 的核心智能体循环 (ReAct)。"""
    def __init__(self, bus, model="local-model", base_url="http://localhost:1234/v1", 
                 api_key="lm-studio",
                 tool_registry: ToolRegistry = None, 
                 session_manager: SessionManager = None,
                 memory_store: MemoryStore = None,
                 subagent_manager=None):
        self.bus = bus
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.tools = tool_registry
        self.session_manager = session_manager
        self.memory_store = memory_store
        self.subagent_manager = subagent_manager
        self.max_turns = 10

    async def run(self):
        logger.info("🧠 [nanocore] 大脑引擎已启动。")
        
        # 加载灵魂与长期记忆
        soul = Path("SOUL.md").read_text() if Path("SOUL.md").exists() else "你是一个助手。"
        user_info = Path("USER.md").read_text() if Path("USER.md").exists() else ""
        long_term_memory = self.memory_store.read() if self.memory_store else ""
        
        base_system_prompt = f"{soul}\n\n{user_info}\n\n"
        base_system_prompt += f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        base_system_prompt += f"工作目录: {os.getcwd()}\n"
        
        if long_term_memory:
            base_system_prompt += f"\n### 长期记忆 (Long-term Memory)\n{long_term_memory}\n"

        base_system_prompt += "\n你可以通过调用工具来执行文件操作、命令及保存记忆。\n"

        while True:
            try:
                incoming = await self.bus.inbound.get()
                user_text = incoming.get('text', '').strip()
                sender = incoming['sender']
                message_id = incoming.get('message_id')
                session_id = sender # 简化处理：以发送者为会话 ID
                
                # 处理 /stop 指令
                if user_text == "/stop":
                    logger.info(f"🧠 [大脑] 收到停止指令来自: {sender}")
                    count = 0
                    if self.subagent_manager:
                        count = await self.subagent_manager.stop_all()
                    
                    await self.bus.outbound.put({
                        "sender": sender,
                        "message_id": message_id,
                        "text": f"⏹ 已停止 {count} 个后台任务并清理上下文。" if count else "⏹ 已清理当前指令集。",
                        "status": "finished"
                    })
                    continue

                if not user_text:
                    continue

                logger.info(f"🧠 [大脑] 收到任务: {user_text}")

                # 1. 加载历史消息
                messages = []
                if self.session_manager:
                    messages = self.session_manager.load(session_id)
                
                if not messages:
                    messages = [{"role": "system", "content": base_system_prompt}]
                else:
                    # 确保 system prompt 始终是最新的（包含最新记忆和时间）
                    messages[0] = {"role": "system", "content": base_system_prompt}
                
                # 发送正在处理反馈
                await self.bus.outbound.put({
                    "sender": sender,
                    "message_id": message_id,
                    "status": "processing"
                })
                
                messages.append({"role": "user", "content": user_text})
                
                # 2. 执行处理 (ReAct 循环)
                final_text = await self._process_turn(messages, sender, message_id)
                
                # 3. 保存并回复
                if self.session_manager:
                    self.session_manager.save(session_id, messages)
                
                await self.bus.outbound.put({
                    "sender": sender,
                    "message_id": message_id,
                    "text": final_text,
                    "status": "finished"
                })
            except Exception as e:
                logger.error(f"❌ [大脑] 处理消息出错 (系统级): {e}")
                # 即使出错也不退出 while True，保证大脑继续运行
                await asyncio.sleep(1)

    async def _process_turn(self, messages, sender, message_id):
        """执行单次对话循环（支持多轮工具调用）。"""
        for turn in range(self.max_turns):
            try:
                openai_tools = self.tools.get_openai_tools() if self.tools else None
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=openai_tools if openai_tools else None
                )
            except Exception as e:
                error_msg = f"LLM 调用出错: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return error_msg

            resp_msg = response.choices[0].message
            if not resp_msg.tool_calls:
                final_text = resp_msg.content or ""
                messages.append({"role": "assistant", "content": final_text})
                return final_text

            # 将 OpenAI 的消息对象转为 dict 存入历史，否则无法 JSON 序列化
            messages.append(resp_msg.model_dump())
            
            for tc in resp_msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                logger.info(f"  ↳ 🛠️  执行工具: {name}({json.dumps(args, ensure_ascii=False)})")
                if self.tools:
                    # 如果工具需要上下文，设置上下文
                    tool_instance = self.tools.get(name)
                    if tool_instance and hasattr(tool_instance, "set_context"):
                        tool_instance.set_context(sender=sender)
                        
                    result = await self.tools.call(name, args)
                else:
                    result = f"错误：未配置工具注册表，无法执行 {name}。"
                messages.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": result})
        return "达到最大思考轮数，未生成最终回复。"

    async def process_direct(self, content: str, sender: str, message_id: str = None) -> str:
        """从外部（如定时任务）直接触发一次大脑处理。"""
        # 1. 设置上下文
        soul = Path("SOUL.md").read_text() if Path("SOUL.md").exists() else "你是一个助手。"
        base_system_prompt = f"{soul}\n\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # 2. 加载会话
        messages = []
        if self.session_manager:
            messages = self.session_manager.load(sender)
        
        if not messages:
            messages = [{"role": "system", "content": base_system_prompt}]
        else:
            messages[0] = {"role": "system", "content": base_system_prompt}
            
        messages.append({"role": "user", "content": content})
        
        # 3. 执行处理
        result = await self._process_turn(messages, sender, message_id)
        
        # 4. 保存会话
        if self.session_manager:
            self.session_manager.save(sender, messages)
            
        return result

if __name__ == "__main__":
    # 独立测试大脑：不需要飞书，直接在终端模拟对话
    async def test_brain():
        from nanocore.bus import MessageBus
        bus = MessageBus()
        brain = AgentBrain(bus)
        
        # 启动大脑（异步运行）
        task = asyncio.create_task(brain.run())
        
        # 模拟喂一条消息
        print("👤 模拟用户输入: 你好，请介绍一下你自己。")
        await bus.inbound.put({"sender": "me", "text": "你好，请介绍一下你自己。"})
        
        # 等待大脑回复
        reply = await bus.outbound.get()
        print(f"🤖 大脑回复: {reply['text']}")
        
        task.cancel() # 测试完关闭

    asyncio.run(test_brain())
