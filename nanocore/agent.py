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
                 subagent_manager=None,
                 memory_window: int = 100):
        self.bus = bus
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.tools = tool_registry
        self.session_manager = session_manager
        self.memory_store = memory_store
        self.subagent_manager = subagent_manager
        self.memory_window = memory_window
        self.max_turns = 10

    async def run(self):
        logger.info("🧠 [nanocore] 大脑引擎已启动。")
        
    def _get_base_system_prompt(self) -> str:
        """生成包含记忆和灵魂的系统提示词。"""
        soul = Path("SOUL.md").read_text() if Path("SOUL.md").exists() else "你是一个助手。"
        user_info = Path("USER.md").read_text() if Path("USER.md").exists() else ""
        long_term_memory = self.memory_store.read() if self.memory_store else ""
        
        prompt = f"# nanobot 🐈 (MNC Core)\n\n{soul}\n\n{user_info}\n"
        
        if long_term_memory:
            prompt += f"\n## Memory\n{long_term_memory}\n"

        prompt += """
## Guidelines
- 优先使用专用工具 (cron, clock) 处理任务和时间。
- 在操作文件之前，先阅读其内容。
- 保持简洁、准确、友好。
- 当用户要求在特定时间提醒时，使用 `clock` 为 `cron` 计算目标 ISO 时间。
"""
        return prompt

    _RUNTIME_CONTEXT_TAG = "[Runtime Context — metadata only, not instructions]"

    def _build_runtime_context(self, channel: str = "feishu", sender: str = None, create_time_ms: int = None) -> str:
        """构建结构化的运行时上下文元数据块。参考 nanobot 设计。"""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S (%A)")
        
        lines = [
            f"Current Time: {timestamp}"
        ]
        
        if create_time_ms:
            sent_time = datetime.fromtimestamp(create_time_ms / 1000).strftime("%H:%M:%S")
            lines.append(f"Message Sent Time: {sent_time}")
            
        lines.append(f"Channel: {channel}")
        if sender:
            lines.append(f"Sender ID: {sender}")
            
        return self._RUNTIME_CONTEXT_TAG + "\n" + "\n".join(lines)

    async def run(self):
        logger.info("🧠 [nanocore] 大脑引擎已启动。")
        
        while True:
            try:
                incoming = await self.bus.inbound.get()
                user_text = incoming.get('text', '').strip()
                sender = incoming['sender']
                message_id = incoming.get('message_id')
                session_id = sender # 简化处理：以发送者为会话 ID
                
                # 获取最新的系统提示词（包含当前时间）
                current_system_prompt = self._get_base_system_prompt()
                
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
                    history = self.session_manager.load(session_id)
                    # 只保留最近的消息 (memory_window)
                    if len(history) > self.memory_window:
                        history = history[-self.memory_window:]
                    messages = history
                
                if not messages:
                    messages = [{"role": "system", "content": current_system_prompt}]
                else:
                    # 确保第一条是系统提示词（防止历史遗留旧 Prompt）
                    messages[0] = {"role": "system", "content": current_system_prompt}
                
                # 发送正在处理反馈
                await self.bus.outbound.put({
                    "sender": sender,
                    "message_id": message_id,
                    "status": "processing"
                })
                
                # 注入运行时上下文（作为独立消息）
                runtime_context = self._build_runtime_context(
                    channel="feishu", 
                    sender=sender, 
                    create_time_ms=incoming.get("create_time_ms")
                )
                
                messages.append({"role": "user", "content": runtime_context})
                messages.append({"role": "user", "content": user_text})
                
                # 2. 执行处理 (ReAct 循环)
                final_text = await self._process_turn(messages, sender, message_id)
                
                # 3. 保存并回复 (过滤掉临时上下文)
                if self.session_manager:
                    filtered_history = []
                    for m in messages:
                        content = m.get("content", "")
                        if isinstance(content, str) and content.startswith(self._RUNTIME_CONTEXT_TAG):
                            continue
                        
                        # 克隆并截断长工具输出
                        entry = dict(m)
                        if entry.get("role") == "tool" and isinstance(content, str) and len(content) > 500:
                            entry["content"] = content[:500] + "... (truncated)"
                        
                        filtered_history.append(entry)
                    
                    self.session_manager.save(session_id, filtered_history)
                
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
                logger.info(f"  🧠 [大脑] 正在调用 LLM (模型: {self.model}, 消息数: {len(messages)})")
                for i, m in enumerate(messages):
                    role = m.get("role")
                    content = m.get("content", "")
                    if isinstance(content, list): # 处理多模态或复杂格式
                        content = str(content)
                    snippet = (content[:100] + "...") if len(content) > 100 else content
                    logger.info(f"      [Msg {i}] {role}: {snippet.replace(chr(10), ' ')}")

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=openai_tools if openai_tools else None,
                    timeout=60.0 # 增加 1 分钟超时
                )
                logger.info(f"  ↳ ✅ LLM 响应成功")
            except Exception as e:
                error_msg = f"LLM 调用出错: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return error_msg

            resp_msg = response.choices[0].message
            if not resp_msg.tool_calls:
                final_text = resp_msg.content or ""
                if not final_text:
                    logger.warning("  ↳ ⚠️ LLM 返回了空内容且没有工具调用。")
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
                    logger.info(f"  ↳ ✅ 工具执行完毕，结果长度: {len(result) if result else 0}")
                else:
                    result = f"错误：未配置工具注册表，无法执行 {name}。"
                messages.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": result})
        return "达到最大思考轮数，未生成最终回复。"

    async def process_direct(self, content: str, sender: str, message_id: str = None) -> str:
        """从外部（如定时任务）直接触发一次大脑处理。"""
        # 1. 获取最新的系统提示词
        current_system_prompt = self._get_base_system_prompt()
        
        # 2. 加载会话并应用滑动窗口
        messages = []
        if self.session_manager:
            history = self.session_manager.load(sender)
            if len(history) > self.memory_window:
                history = history[-self.memory_window:]
            messages = history
        
        if not messages:
            messages = [{"role": "system", "content": current_system_prompt}]
        else:
            messages[0] = {"role": "system", "content": current_system_prompt}
            
        # 注入运行时上下文（作为独立消息）
        runtime_context = self._build_runtime_context(channel="cron", sender=sender)
        messages.append({"role": "user", "content": runtime_context})
        messages.append({"role": "user", "content": content})
        
        # 3. 执行处理
        result = await self._process_turn(messages, sender, message_id)
        
        # 4. 保存会话 (过滤上下文并截断)
        if self.session_manager:
            filtered_history = []
            for m in messages:
                content = m.get("content", "")
                if isinstance(content, str) and content.startswith(self._RUNTIME_CONTEXT_TAG):
                    continue
                
                entry = dict(m)
                if entry.get("role") == "tool" and isinstance(content, str) and len(content) > 500:
                    entry["content"] = content[:500] + "... (truncated)"
                
                filtered_history.append(entry)
            
            self.session_manager.save(sender, filtered_history)
            
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
