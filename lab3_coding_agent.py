import asyncio
from openai import AsyncOpenAI
import json

# 1. 连接到你的 LM Studio
client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# 2. 定义“编码工具箱” (模仿 nanobot 的核心能力)
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_code",
            "description": "读取指定文件的源代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名，例如 'app.py'"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_code",
            "description": "修改或重写文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名"},
                    "code": {"type": "string", "description": "新的代码内容"}
                },
                "required": ["filename", "code"]
            }
        }
    }
]

async def core_loop():
    messages = [
        {"role": "system", "content": "你是一个专业的编码助手。你会先读取代码分析问题，然后再写出修复后的代码。"}
    ]
    
    # 模拟一个“带 Bug”的本地环境
    virtual_fs = {
        "hello.py": "def say_hello():\n    print('Hello World')\n    # 这里的函数缺少返回值"
    }

    print("👩‍💻 编码智能体已上线。试试输入：'帮我给 hello.py 加上返回值并将问候语改为中文'")

    while True:
        user_input = input("\n👤 用户指令: ")
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        
        max_turns = 5
        turn = 0
        
        while turn < max_turns:
            turn += 1
            print(f"💡 思考中 (第 {turn} 轮)...")
            
            response = await client.chat.completions.create(
                model="local-model",
                messages=messages,
                tools=tools,
            )

            response_message = response.choices[0].message
            
            if not response_message.tool_calls:
                final_answer = response_message.content
                print(f"\n🤖 助手总结: {final_answer}")
                messages.append({"role": "assistant", "content": final_answer})
                break 

            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                # 兼容处理参数
                if isinstance(tool_call.function.arguments, str):
                    args = json.loads(tool_call.function.arguments)
                else:
                    args = tool_call.function.arguments
                
                print(f"🛠️  执行动作: {function_name}({args.get('filename', '')})")
                
                # --- 模拟文件读写逻辑 ---
                if function_name == "read_code":
                    filename = args.get("filename")
                    content = virtual_fs.get(filename, "文件不存在")
                    result = f"--- {filename} 内容 ---\n{content}"
                elif function_name == "write_code":
                    filename = args.get("filename")
                    code = args.get("code")
                    virtual_fs[filename] = code
                    result = f"成功写入文件 {filename}。"
                else:
                    result = "未知命令。"
                
                print(f"📦 得到反馈: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result
                })
        
        if turn >= max_turns:
            print("⚠️ 任务链过长。")

if __name__ == "__main__":
    asyncio.run(core_loop())
