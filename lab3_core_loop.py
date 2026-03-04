import asyncio
from openai import AsyncOpenAI
import json

# 1. 连接到你的 LM Studio
client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# 2. 定义我们的“工具箱”说明书 (隐式拆解的关键)
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "在网页上搜索信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        }
    }
]

async def core_loop():
    messages = [
        {"role": "system", "content": "你是一个全能助手。你可以通过拆解任务，分步骤调用不同的工具来解决复杂问题。"}
    ]
    
    print("🤖 智能体已上线（支持“走一步看一步”的隐式拆解）。输入 'quit' 退出。")

    while True:
        user_input = input("\n👤 你: ")
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        
        # --- [核心] 隐式拆解逻辑：ReAct 循环 ---
        max_turns = 5 # 限制最多思考 5 轮，防止死循环
        turn = 0
        
        while turn < max_turns:
            turn += 1
            print(f"💡 思考中 (第 {turn} 轮)...")
            
            # 询问 AI 下一步干什么
            response = await client.chat.completions.create(
                model="local-model",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            
            # 情况 A：AI 觉得不需要工具了，准备直接回答
            if not response_message.tool_calls:
                final_answer = response_message.content
                print(f"\n🤖 助手: {final_answer}")
                messages.append({"role": "assistant", "content": final_answer})
                break 

            # 情况 B：AI 决定使用工具 (拆解任务的第一步或中间步)
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                # 兼容不同模型的参数传递方式
                if isinstance(tool_call.function.arguments, str):
                    args = json.loads(tool_call.function.arguments)
                else:
                    args = tool_call.function.arguments
                
                print(f"🛠️  执行动作: {function_name}({args})")
                
                # 模拟工具的真实运行结果
                if function_name == "read_file":
                    result = f"文件 {args['filename']} 的内容是：‘请帮我查一下 2026 冬奥会吉祥物。’"
                elif function_name == "web_search":
                    result = f"搜索 '{args['query']}' 的结果：2026冬奥会吉祥物是白鼬 Milo 和 Maya。"
                else:
                    result = "未知工具。"
                
                print(f"📦 得到反馈: {result}")

                # 把“动作”和“观察结果”都记在记忆里，回到 while 开头让 AI 继续思考
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                })
        
        if turn >= max_turns:
            print("⚠️ 任务太烧脑，AI 思考轮数达到上限。")

if __name__ == "__main__":
    asyncio.run(core_loop())
