# mynanocloud (MNC): A Minimal Cloud Agent

MNC 是一个极简的 AI Agent 框架，基于 `nanobot` 的核心理念构建。

它的设计哲学是 **"Zero Magic"**：没有复杂的黑盒框架，只有清晰的 Python 代码和 Docker 沙箱。本项目不仅是一个机器人，更是一套手把手的智能体开发课程，旨在帮助你从零掌握 Agent 的底层原理。

---

## 智能体的解构 (Anatomy of MNC)

在 MNC 中，一个智能体被拆解为三个最基础的概念：

1. **The Bus (消息总线)**: 异步的通信枢纽，负责在大脑和外部世界之间传递消息。
2. **The Brain (大脑)**: 核心思考循环 (ReAct Loop)，负责解析任务、调用工具并决策。
3. **The Connector (连接器)**: 智能体的感官与手脚（如飞书、终端），负责与用户交互。

---

## 核心循环 (The Thinking Loop)

Agent 的逻辑其实就是一个简单的 Loop。在 `nanocore/agent.py` 中，这就是它的全部秘密：

```python
while True:
    # 1. 获取任务
    user_text = await self.bus.inbound.get()
    
    # 2. 思考与行动 (ReAct)
    for turn in range(self.max_turns):
        response = await self.query_lm(messages)
        
        # 如果是普通的回复，结束循环
        if not response.tool_calls:
            await self.reply(response.content)
            break
            
        # 如果是工具调用，执行并返回结果
        for call in response.tool_calls:
            result = await self.tools.execute(call.name, call.args)
            messages.append({"role": "tool", "content": result})
```

---

## 插件化工具箱 (No-Magic Tooling)

MNC 放弃了复杂的装饰器，采用纯粹的 OOP 模式来管理工具。每一个工具都是一个标准的类：

- **FileSystem**: `read_file`, `write_file`, `edit_file` (精准编辑)。
- **Shell**: `exec` (具备安全黑名单的命令执行)。
- **Persistence**: `save_memory` (AI 自我记忆巩固)。

---

## 安全沙箱 (The Sandbox)

为了防止 AI 搞破坏，MNC 默认在 **Docker 容器**中运行。这意味着：
- **物理隔离**: AI 只能访问容器内的文件系统。
- **环境受控**: 即使执行了 `rm -rf /`，也只会毁掉一个临时的容器。
- **安全审计**: `ExecTool` 具备命令过滤机制。

---

## 快速开始

### 1. 准备环境
确保安装了 Docker 和 Docker Compose。

### 2. 启动
```bash
docker-compose up --build -d
```
机器人将连接到飞书/Slack，并使用 `host.docker.internal:1234` 调用你的本地 LLM (如 LM Studio)。

### 3. 连接 Slack (Socket Mode)
1. 在 [Slack API](https://api.slack.com/apps) 创建 App，开启 **Socket Mode** 获取 `xapp-` Token。
2. 在 **OAuth & Permissions** 添加 `chat:write`, `im:history`, `reactions:add` 等权限。
3. 在 **Event Subscriptions** 开启并订阅 `message.im` 等事件。
4. 在 **App Home** 开启 **Messages Tab**。
5. 获取 `xoxb-` Bot Token。
6. 将 Token 填入 `.env` 中的 `SLACK_BOT_TOKEN` 和 `SLACK_APP_TOKEN`。

---

## 学习目标 (Mission)

- **解构核心逻辑**: 理解异步驱动与 ReAct 循环。
- **掌握工业架构**: 学习如何平衡解构的简洁性与系统的扩展性。
- **能力自主进化**: 探索 AI 如何通过 `edit_file` 动态修改自身代码。

---

MIT License. 基于对 `nanobot` 的学习与致敬。
