# nanobot Mastery Plan (Python Beginner to Expert)

This plan is designed to take you from a Python beginner to a "master" of the `nanobot` project. We will progress from running the code to understanding its soul, and finally to extending it with your own ideas.

## Proposed Learning Journey

---

### Phase 1: Foundation (The User Experience)
**Goal:** Understand what `nanobot` does by using it.
- **Onboarding:** Run `nanobot onboard` and explore the `~/.nanobot/config.json`.
- **Interaction:** Use the CLI `nanobot agent` to chat and test basic skills.
- **Observation:** Watch the logs to see how it "thinks" (tool calls, reasoning).

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
