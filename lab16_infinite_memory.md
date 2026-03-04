# Lab 16: 永恒记忆 (Session & Persistence) 🧠

在这个实验中，我们将打破“重启即失忆”的魔咒。我们将为 `mynanocloud` 实现一套与 `nanobot` 核心一致的持久化方案。

## 1. 目标 (Learning Objectives)
- **Session 管理**：学习如何将实时对话序列化并存储为 JSON。
- **长期记忆 (Memory)**：实现一个 `MEMORY.md` 文件，让 AI 能够存取跨会话的事实。
- **记忆巩固 (Consolidation)**：通过 `save_memory` 工具，实现 AI 的“自我总结”能力。

## 2. 核心逻辑

### 2.1 SessionManager (`nanocore/session.py`)
负责加载和同步对话列表：
```python
def load_session(session_id):
    # 读取 data/sessions/{session_id}.json
def save_session(session_id, messages):
    # 写入文件
```

### 2.2 MemoryStore
这是一个极简的长期记忆层。在系统启动时，我们会读取 `MEMORY.md` 并将其插入到 System Prompt 中。

### 2.3 save_memory 工具
我们将新增一个工具，让 AI 决定什么时候需要把信息从“内存”（短期对话）沉淀到“硬盘”（长期记忆）。

## 3. 实验步骤

### Step 1: 创建存储目录
在根目录下建立 `data/sessions/`。

### Step 2: 实现 Session 模块
编写 `nanocore/session.py`。

### Step 3: 更新 AgentBrain
将 `AgentBrain` 里的 `messages` 改为从 `SessionManager` 加载，并在每一轮对话后自动触发保存。

### Step 4: 实现 Memory 工具
编写 `nanocore/tools/memory.py`，允许 AI 修改 `MEMORY.md`。

## 4. 为什么这么做？ (The PAYOFF)
从此以后，你可以对机器人说：“记住，我的开发环境是 Mac，我以后只想写 Python 代码。”
重启机器人后，它依然会记得这个约定。

**准备好赋予你的机器人“永恒灵魂”了吗？🐈💾✨**
