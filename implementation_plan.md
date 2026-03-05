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
