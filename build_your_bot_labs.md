# 🛠️ 《从零开始：构建你的 AI 智能体》实验手册 (Lab Series)

本手册将引导学员从一个空白文件夹开始，一步步实现 `nanobot` 的核心逻辑。

---

## 📅 实验 1：打下地基 (Project Setup)
**目标**：建立工程结构，理解 Python 包的概念。
1.  **新建文件夹**：`mkdir mybot && cd mybot`
2.  **创建入口**：新建 `main.py`。
3.  **安装核心库**：`pip install openai` (我们先用标准库作为基础)。
4.  **【思考】**：为什么我们要分文件夹存放代码？（引入模块化思想）。

---

## 🧠 实验 2：第一次对话 (The First Hello)
**目标**：连接 AI 大脑。
1.  **编写代码**：在 `main.py` 中写一个简单的函数，调用 OpenAI API。
2.  **环境变量**：学习如何安全地存储 API Key，不直接写在代码里。
3.  **【挑战】**：让 AI 以“古代诗人”的语气和你打招呼。

---

## 🔄 实验 3：核心循环 (The Loop)
**目标**：实现 `nanobot` 的灵魂——无限思考循环。
1.  **编写 `while` 循环**：让对话不再是“一问一答”就结束。
2.  **打印日志**：学习使用 [print](file:///Users/peng/Documents/code/2026-personal-workspace/nanobot/nanobot/cli/commands.py#100-108) 或 `logger` 观察 AI 的“思考过程”。
3.  **【挑战】**：给循环加一个“退出键”，比如输入 [exit](file:///Users/peng/Documents/code/2026-personal-workspace/nanobot/nanobot/cli/commands.py#504-508) 就结束程序。

---

## 🛠️ 实验 4：工具箱 (The Tool Registry)
**目标**：定义什么是“工具”。
1.  **定义函数**：写一个简单的 `get_weather(city)` 函数。
2.  **描述工具**：学习如何用 JSON 格式给这个函数写“说明书”，告诉 AI 怎么用它。
3.  **【代码】**：创建一个 `tools.py`，专门存放这些“超能力”。

---

## ⚡ 实验 5：执行工具 (Tool Execution)
**目标**：实现最难的一步——让 AI 真的去用工具。
1.  **解析指令**：当 AI 回复 `tool_calls` 时，编写 Python 代码解析它想用哪个工具。
2.  **反射机制**：使用 Python 的 `getattr` 动态调用函数（这是 `nanobot` 的核心技巧）。
3.  **【挑战回传】**：把工具运行的结果，再传回给 AI，让它总结成一句话告诉用户。

---

## 🚀 实验 6：进阶与整合 (Integration)
**目标**：让你的 Bot 拥有持久记忆。
1.  **管理上下文**：学习如何用一个 [list](file:///Users/peng/Documents/code/2026-personal-workspace/nanobot/nanobot/cli/commands.py#783-834) 存储对话历史，不让 AI “转头就忘”。
2.  **清理记忆**：如果对话太长了怎么办？（引入简单的截断逻辑）。

---

## 📝 给老师的建议：
*   **每一步都可运行**：确保学员在每个实验结束时，都能看到一个“看得见”的结果。
*   **对比学习**：让学员对比自己写的 50 行代码和 `nanobot` 的 4000 行代码，理解“工程化”和“健壮性”的区别。
