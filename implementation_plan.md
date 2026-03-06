# nanobot Mastery Plan (Python Beginner to Expert)

This plan is designed to take you from a Python beginner to a "master" of the `nanobot` project. We will progress from running the code to understanding its soul, and finally to extending it with your own ideas.

## Proposed Learning Journey

---

### Phase 1: Foundation (The User Experience)
**Goal:** Understand what `nanobot` does by using it.
- **Onboarding:** Run `nanobot onboard` and explore the `~/.nanobot/config.json`.
- **Interaction:** Use the CLI `nanobot agent` to chat and test basic skills.
- **Observation:** Watch the logs to see how it "thinks" (tool calls, reasoning).

### Phase 19: Git Commit [DONE]
- **[DONE]**: All changes committed with a structured message.
- **[VERIFY]**: Trigger a task like "5 mins from now" multiple times and verify the base time in the system prompt matches the actual current clock.

### Phase 26: Message Creation Time Injection [NEW]
- **[MODIFY] nanocore/connectors/feishu.py**: Extract `create_time` from the event and pass it to the bus.
- **[MODIFY] nanocore/agent.py**: Use the passed `create_time` to label the user's message as "Message Sent Time" instead of "Message Arrival Time".
- [VERIFY]**: Check logs to see if the AI acknowledges the difference between arrival and creation time.

### Phase 27: Clock Tool Implementation [NEW]
- **[NEW] [clock.py](file:///Users/peng/Documents/code/2026-personal-workspace/mynanocloud/nanocore/tools/clock.py)**: Provide `now` and `delta` (relative time calc) actions.
- **[MODIFY] [lab8_framework_bot.py](file:///Users/peng/Documents/code/2026-personal-workspace/mynanocloud/lab8_framework_bot.py)**: Register `ClockTool`.
- **[VERIFY]**: Trigger "5 mins later" and verify AI uses `clock` tool instead of `exec`.

### Phase 28: Tool Discipline & Prompt Hardening [NEW]
- **[MODIFY] nanocore/agent.py**: Update `_get_base_system_prompt` to include strict guidelines on using high-level tools over raw `exec`/`cat` for managed services.
- **Rules to enforce**:
    - **Tool-First**: Always prefer high-level tools (cron, clock) over raw shell commands.
    - **No Redundancy**: Do not manually inspect data files (e.g., jobs.json) if a tool (e.g., cron list) exists.
    - **Precision**: Use `clock` for all time-related calculations.
- **[VERIFY]**: Ask "What tasks are scheduled?" and verify AI only uses `cron list`.

### Phase 29: Runtime Context Injection [DONE]
- **[MODIFY] nanocore/agent.py**: Implement `_build_runtime_context` helper to generate a structured metadata block.
- **[MODIFY] nanocore/agent.py**: Update `run` and `process_direct` to prepend `[Runtime Context]` (Time, Channel, Sender) to user messages.
- **[VERIFY]**: Check logs for correctly formatted context block.

### Phase 30: nanobot Behavior Alignment [DONE]
- **Goal**: Resolve why the same model performs better in `nanobot` by aligning implementation details.
- **[MODIFY] nanocore/agent.py**: 
    - Split the single joined user message into **two separate user messages** (Context message + Input message) in `run` and `process_direct`.
    - Change context tag to `[Runtime Context — metadata only, not instructions]` to match `nanobot`.
    - Simplify the System Prompt in `_get_base_system_prompt` to be less restrictive/prohibitive and more example-driven.
- **[MODIFY] nanocore/tools/shell.py & clock.py**: Simplify descriptions to avoid "pink elephant" effects and focus on intent.
- **[VERIFY]**: Ask MNC to "remind me in 1 minute" and verify it uses the context to calculate time correctly without resorting to `exec + python`.

### Phase 31: Memory Thinning & Windowing [DONE]
- **Goal**: Prevent session history bloat and maintain performance like `nanobot`.
- **[MODIFY] nanocore/agent.py**: 
    - Add `memory_window` parameter to `AgentBrain` (default 100).
    - Update `run` and `process_direct` to only take the last `memory_window` messages from history.
    - Update the session saving logic to **exclude** messages starting with `[Runtime Context]`.
- **[VERIFY]**: Send 3 messages, check `data/sessions/` files, and verify `[Runtime Context]` is NOT stored while user/assistant/tool messages are.

### Phase 34: Global Media Control Tool (v2)
    - **Goal**: Simulate hardware media keys (F7, F8, F9) for global control.
    - **[NEW] nanocore/tools/media.py**: Implement `MediaTool` using `osascript` with `key code` 100, 101, 103, etc.
    - **[MODIFY] lab8_framework_bot.py**: Register `MediaTool`.

### Phase 35: Debugging LLM connectivity (502 Error)
    - **[MODIFY] lab8_framework_bot.py**: Added `load_dotenv()` to ensure `.env` file is loaded during native execution.
    - **Cleaning**: Cleared `data/sessions/` to resolve context conflicts with deleted tools.

### Phase 36: Optimize MediaTool for Background/Shortcut Execution
    - **Goal**: Use background-friendly commands for Spotify/Music and specific global shortcuts for NeteaseMusic.
    - **[MODIFY] nanocore/tools/media.py**: 
        - For **NeteaseMusic**: Use `keystroke " " using {control down, option down}` for `play_pause`.
        - For **Spotify/Music**: Continue using direct `playpause` background commands.
        - Ensure `app_name` correctly routes to these specific implementations.

### Phase 20: Scheduler Precision [DONE]
- **[MODIFY] nanocore/cron.py**: Modified `_execute_job` to calculate the next run time relative to the *intended* start time (`job.state.next_run_at_ms`) rather than the *actual* finish time, eliminating cumulative drift.

### Phase 16: Session & Persistence [DONE]
- **[NEW] nanocore/session.py**: Implemented a simple file-based `SessionManager`.
- **[MODIFY] nanocore/agent.py**: Updated `AgentBrain` to fetch/store history from `SessionManager`.
- **[MODIFY] lab8_framework_bot.py**: Fixed `SessionManager` instantiation with `data/sessions` path.

### Phase 23: Ollama Integration [NEW]
- **[MODIFY] .env**: Set `LM_STUDIO_URL` to Ollama endpoint and add `LM_MODEL`.
- **[MODIFY] lab8_framework_bot.py**: Enable dynamic model loading from environment.
- **[MODIFY] docker-compose.yml**: Map environment variables from host to container.

### Phase 21: Job Removal Safety [DONE]
- **[MODIFY] nanocore/cron.py**: Updated `remove_job` to explicitly cancel and remove tasks from `_job_tasks` when a job is deleted.
- **[MODIFY] nanocore/cron.py**: Added `run_job` method for manual triggering and testing.
- **[MODIFY] nanocore/cron.py**: Added logic to clean up `_job_tasks` after one-shot jobs complete.

### Phase 22: Batch Job Removal [DONE]
- **[MODIFY] nanocore/cron.py**: Add `clear_jobs()` method to stop and remove all tasks at once.
- **[MODIFY] nanocore/tools/cron.py**: Add `remove_all` action to provide AI with a robust way to fulfill clearing requests.

### Phase 24: Clock-Aligned Intervals [NEW]
- **[MODIFY] nanocore/cron.py**: Update `_compute_next_run` for `every` kind to align with the unix epoch (clock-aligned) if the interval is a round number (e.g., minutes).
- **[MODIFY] nanocore/tools/cron.py**: Update tool description to guide AI on using `cron` for complex clock-alignment or `every` for simple aligned intervals.
- **[STRATEGY] Human-in-the-loop**: Instruct the AI (via tool metadata) to **ask for clarification** if the user's intent is ambiguous (e.g., "Do you want this to start exactly at the next 5-minute mark, or 5 minutes from now?").

### Phase 2: The Core Anatomy (How it Breathes)
**Goal:** Map out the 4,000 lines of code.
- **Entry Points:** Study [nanobot/__main__.py](file:///Users/peng/Documents/code/2026-personal-workspace/nanobot/nanobot/__main__.py) and `nanobot/cli/`.
- **The Brain:** Explore `nanobot/agent/` to see how it processes messages and decides which tools to use.
- **The Memory:** Look at `nanobot/session/` to understand how it remembers the conversation.

### Phase 3: Connectors (The Senses & Voice)
**Goal:** Understand how `nanobot` talks to the world.
- **Providers:** Explore `nanobot/providers/` (Anthropic, DeepSeek, etc.). Learn how it translates user intent into LLM-readable prompts.
- **Channels:** Pick one channel (e.g., `telegram` or `feishu` in `nanobot/channels/`) and see how it handles incoming/outgoing messages.

### Phase 4: Hands-on Extension (Building Your Own)
**Goal:** Modify the codebase.
- **New Skill:** Write a simple "Skill" in `nanobot/skills/` (e.g., a currency converter or a personalized news fetcher).
- **New Provider:** Add a mock provider or a local model provider by following the `Provider Registry` pattern.

### Phase 5: Advanced Mastery (Research & Optimization)
**Goal:** Contribute to the project.
- **Performance:** Run benchmarks or analyze the "Heartbeat" mechanism.
- **Security:** Review `SECURITY.md` and check how session poisoning is prevented.
- **Scaling:** Understand the `bus` (event bus) and how it coordinates multi-channel scenarios.

---

## Verification Plan

### Milestone 1: Environment Ready
- [ ] Run `python -m nanobot --version` and get a valid version.
- [ ] Successfully chat with the bot in CLI mode.

### Milestone 2: Code Literacy
- [ ] Explain the relationship between `Agent`, `Provider`, and `Channel` to your "team".

### Milestone 3: Personalization
- [ ] Successfully implement and run a custom "Hello World" skill.

## User Review Required

> [!IMPORTANT]
> Since you are a Python beginner, we will use a "Read-Explain-Try" cycle for each module.
> **Do you want to start with Phase 1 immediately, or should we adjust the focus (e.g., more focus on AI agent logic vs. more focus on chat platform integration)?**
