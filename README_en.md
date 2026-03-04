# mynanocloud (MNC): A Minimal Cloud Agent

MNC is a minimalist AI Agent framework built on the core principles of `nanobot`.

Its design philosophy is **"Zero Magic"**: no bloated frameworks or black-box abstractions—just clean Python code and a solid Docker sandbox. This project is not just a bot; it's a hands-on curriculum designed to help you master the inner workings of AI Agents from the ground up.

---

## Anatomy of MNC

In MNC, an agent is deconstructed into three foundational concepts:

1. **The Bus**: An asynchronous communication hub that routes messages between the Brain and the outside world.
2. **The Brain**: The core Thinking Loop (ReAct Loop) responsible for parsing tasks, calling tools, and making decisions.
3. **The Connector**: The agent's senses and limbs (e.g., Feishu/Lark, Terminal) that handle interaction with users.

---

## The Thinking Loop

An AI Agent's logic is fundamentally just a simple loop. In `nanocore/agent.py`, this is where the magic (or lack thereof) happens:

```python
while True:
    # 1. Fetch the task
    user_text = await self.bus.inbound.get()
    
    # 2. Think & Act (ReAct)
    for turn in range(self.max_turns):
        response = await self.query_lm(messages)
        
        # If it's a plain response, end the loop
        if not response.tool_calls:
            await self.reply(response.content)
            break
            
        # If it's a tool call, execute and return the result
        for call in response.tool_calls:
            result = await self.tools.execute(call.name, call.args)
            messages.append({"role": "tool", "content": result})
```

---

## No-Magic Tooling

MNC skips complex decorators in favor of a pure OOP pattern for tool management. Every tool is a standard class:

- **FileSystem**: `read_file`, `write_file`, `edit_file` (precision surgical editing).
- **Shell**: `exec` (command execution with a security deny-list).
- **Persistence**: `save_memory` (AI self-driven memory consolidation).

---

## The Sandbox

To keep the AI's "creativity" within bounds, MNC runs by default inside a **Docker container**. This ensures:
- **Physical Isolation**: The AI only has access to the container's filesystem.
- **Controlled Environment**: Even an accidental `rm -rf /` only destroys a temporary instance.
- **Security Auditing**: The `ExecTool` includes active command filtering.

---

## Quick Start

### 1. Prepare Environment
Ensure you have Docker and Docker Compose installed.

### 2. Start
```bash
docker-compose up --build -d
```
The bot will connect to Feishu and use `host.docker.internal:1234` to talk to your local LLM (e.g., LM Studio).

---

## Learning Objectives (The Mission)

- **Deconstruct Core Logic**: Understand asynchronous drivers and ReAct loops.
- **Master Industrial Architecture**: Learn to balance minimalist design with high extensibility.
- **Autonomous Evolution**: Explore how AI can dynamically modify its own code via `edit_file`.

---

MIT License. Developed with respect for and inspired by `nanobot`.
