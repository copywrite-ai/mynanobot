# Lab 15: 瑞士军刀 (Tool Registry) 🛠️

在这个实验中，我们将把 `mynanocloud` 的“双手”从硬编码的逻辑重构为一个专业的、插件化的工具系统。

## 1. 目标 (Learning Objectives)
- **解耦工具逻辑**：将 `AgentBrain` 中的 `if name == "read_file"` 彻底移除。
- **面向对象编程 (OOP)**：使用基类 (Base Class) 定义工具的标准接口。
- **自动 Schema 生成**：让工具自己告诉 AI 它们需要什么参数。
- **能力扩展**：实现 `WriteFileTool`, `ListDirTool` 和一个带审计的 `ExecTool`。

## 2. 核心组件 (Core Architecture)

我们将引入一个新的模块 `nanocore/tools/base.py`：

```python
class BaseTool:
    name: str
    description: str
    parameters: dict

    async def execute(self, **kwargs) -> str:
        raise NotImplementedError
```

还有一个 **ToolRegistry** 用于管理：
- `get_openai_tools()`: 生成给 OpenAI 的 JSON Schema。
- `call(name, args)`: 根据名字动态调用对应的工具类。

## 3. 实验步骤 (Lab Steps)

### Step 1: 定义基类
创建 `nanocore/tools/base.py`，定义工具的“协议”。

### Step 2: 实现文件工具
创建 `nanocore/tools/filesystem.py`：
- `ReadFileTool`: 读文件。
- `WriteFileTool`: 写文件（这是 AI 第一次获得“修改世界”的能力）。
- `ListDirTool`: 查目录。

### Step 3: 实现 Shell 工具
创建 `nanocore/tools/shell.py`：
- `ExecTool`: 运行命令。注意：在 Docker 内部运行，安全性比直接运行高得多，但我们依然要加黑名单。

### Step 4: 重构 AgentBrain
让 `AgentBrain` 接受一个 `ToolRegistry` 对象，并在收到 `tool_calls` 时：
```python
# 伪代码：未来的 AgentBrain
for tc in resp_msg.tool_calls:
    result = await registry.call(tc.function.name, tc.function.arguments)
```

## 4. 为什么这么做？ (The PAYOFF)
有了这套系统，你想给机器人加任何新能力（比如搜索网页、查数据库），只需要写一个新的类并放进 Registry，完全不需要动 `AgentBrain` 的核心逻辑。

**准备好把你的机器人变成“瑞士军刀”了吗？** 🐕🔧
