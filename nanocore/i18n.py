import os
from dotenv import load_dotenv

load_dotenv()
BOT_LANGUAGE = os.getenv("BOT_LANGUAGE", "zh")

STRINGS = {
    "zh": {
        "agent_starting": "🧠 [nanocore] 大脑引擎已启动。",
        "agent_stop_received": "🧠 [大脑] 收到停止指令来自: {sender}",
        "agent_task_received": "🧠 [大脑] 收到任务: {text}",
        "agent_error_system": "❌ [大脑] 处理消息出错 (系统级): {e}",
        "agent_calling_llm": "  🧠 [大脑] 正在调用 LLM (模型: {model}, 消息数: {count})",
        "agent_llm_success": "  ↳ ✅ LLM 响应成功",
        "agent_llm_empty": "  ↳ ⚠️ LLM 返回了空内容且没有工具调用。",
        "agent_executing_tool": "  ↳ 🛠️  执行工具: {name}({args})",
        "agent_tool_finished": "  ↳ ✅ 工具执行完毕，结果长度: {len}",
        
        "feishu_missing": "⚠️ [Feishu] 未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET，飞书通道未启动。",
        "slack_missing": "⚠️ [Slack] 未配置 SLACK_BOT_TOKEN 或 SLACK_APP_TOKEN，Slack 通道未启动。",
        "starting": "✨ [mynanocloud] 极简框架版启动中...",
        "shutdown": "\n👋 机器人已安全关闭。",
        
        "session_dir": "💾 [Session] 会话存储目录: {dir}",
        "session_load_fail": "❌ [Session] 加载会话 {key} 失败: {e}",
        "session_save_fail": "❌ [Session] 保存会话 {key} 失败: {e}",
        "session_deleted": "🗑️ [Session] 已删除会话: {key}",
        
        "feishu_starting": "🚀 [nanocore] 飞书连接已启动。",
        "feishu_ws_disconnected": "⚠️ [飞书] WebSocket 异常断开: {e}",
        "feishu_msg_received": "📥 [飞书] 收到来自 {sender} 的消息: '{text}' (ID: {id}, 诞生于: {time})",
        "feishu_reaction_fail": "❌ [飞书] 发送表情 {type} 失败: {code} - {msg}",
        "feishu_reaction_error": "⚠️ [飞书] 发送表情 {type} 触发异常: {e}",
        "feishu_send_fail": "❌ [飞书] 推送消息失败: {code} - {msg} (目标: {target})",
        "feishu_send_success": "✅ [飞书] 消息推送成功 (目标: {target})",
        
        "slack_starting": "🚀 [nanocore] Slack Socket Mode connector starting...",
        "slack_init": "✅ [nanocore] Slack Socket Mode connector initialized.",
        "slack_msg_received": "📥 [Slack] Message from {user} in {channel}: '{text}' (TS: {ts})",
        "slack_reaction_fail": "⚠️ [Slack] Failed to add reaction: {e}",
        "slack_send_success": "✅ [Slack] Message sent to {channel}",
        "slack_send_fail": "❌ [Slack] Failed to send message: {e}",
        
        "subagent_starting": "🚀 [SubagentManager] 已启动子代理 [{id}]: {label}",
        "subagent_executing": "⏳ [Subagent] 子代理 {id} 开始执行: {label}",
        "subagent_finished": "✅ [Subagent] 子代理 {id} 顺利完成。",
        "subagent_interrupted": "🛑 [Subagent] 子代理 {id} 被强制中断。",
        "subagent_error": "❌ [Subagent] 子代理 {id} 执行出错: {e}",
        "subagent_stopped_count": "⏹ [SubagentManager] 已停止 {count} 个运行中的任务。",
        
        "cron_load_fail": "⚠️ [Cron] 加载失败: {e}",
        "cron_starting": "⏰ [Cron] 服务已启动，包含 {count} 个任务。",
        "cron_skipping": "⏭️ [Cron] 任务仍在执行，跳过本次重入: {name} ({id})",
        "cron_triggering": "⚡️ [Cron] 正在触发任务: {name} ({id})",
        "cron_fail": "❌ [Cron] 任务执行失败: {e}",
        "cron_removed": "🚫 [Cron] 已强行停止并移除任务: {id}",
        "cron_cancelled": "🚫 [Cron] 已取消正在运行的任务: {id}",
        "cron_cleared": "🧹 [Cron] 已清空所有任务 (共 {count} 个)"
    },
    "en": {
        "agent_starting": "🧠 [nanocore] Brain engine started.",
        "agent_stop_received": "🧠 [Brain] Stop command received from: {sender}",
        "agent_task_received": "🧠 [Brain] Task received: {text}",
        "agent_error_system": "❌ [Brain] Message processing error (System Level): {e}",
        "agent_calling_llm": "  🧠 [Brain] Calling LLM (Model: {model}, Messages: {count})",
        "agent_llm_success": "  ↳ ✅ LLM response successful",
        "agent_llm_empty": "  ↳ ⚠️ LLM returned empty content without tool calls.",
        "agent_executing_tool": "  ↳ 🛠️  Executing tool: {name}({args})",
        "agent_tool_finished": "  ↳ ✅ Tool execution finished, result length: {len}",
        
        "feishu_missing": "⚠️ [Feishu] FEISHU_APP_ID or FEISHU_APP_SECRET not configured. Feishu connector skipped.",
        "slack_missing": "⚠️ [Slack] SLACK_BOT_TOKEN or SLACK_APP_TOKEN not configured. Slack connector skipped.",
        "starting": "✨ [mynanocloud] Minimal framework starting...",
        "shutdown": "\n👋 Bot has been safely shut down.",
        
        "session_dir": "💾 [Session] Session storage directory: {dir}",
        "session_load_fail": "❌ [Session] Failed to load session {key}: {e}",
        "session_save_fail": "❌ [Session] Failed to save session {key}: {e}",
        "session_deleted": "🗑️ [Session] Session deleted: {key}",
        
        "feishu_starting": "🚀 [nanocore] Feishu connector started.",
        "feishu_ws_disconnected": "⚠️ [Feishu] WebSocket disconnected unexpectedly: {e}",
        "feishu_msg_received": "📥 [Feishu] Message from {sender}: '{text}' (ID: {id}, Created at: {time})",
        "feishu_reaction_fail": "❌ [Feishu] Failed to send reaction {type}: {code} - {msg}",
        "feishu_reaction_error": "⚠️ [Feishu] Exception while sending reaction {type}: {e}",
        "feishu_send_fail": "❌ [Feishu] Failed to push message: {code} - {msg} (Target: {target})",
        "feishu_send_success": "✅ [Feishu] Message pushed successfully (Target: {target})",
        
        "slack_starting": "🚀 [nanocore] Slack Socket Mode connector starting...",
        "slack_init": "✅ [nanocore] Slack Socket Mode connector initialized.",
        "slack_msg_received": "📥 [Slack] Message from {user} in {channel}: '{text}' (TS: {ts})",
        "slack_reaction_fail": "⚠️ [Slack] Failed to add reaction: {e}",
        "slack_send_success": "✅ [Slack] Message sent to {channel}",
        "slack_send_fail": "❌ [Slack] Failed to send message: {e}",
        
        "subagent_starting": "🚀 [SubagentManager] Started sub-agent [{id}]: {label}",
        "subagent_executing": "⏳ [Subagent] Sub-agent {id} started execution: {label}",
        "subagent_finished": "✅ [Subagent] Sub-agent {id} completed successfully.",
        "subagent_interrupted": "🛑 [Subagent] Sub-agent {id} was forcibly interrupted.",
        "subagent_error": "❌ [Subagent] Sub-agent {id} execution error: {e}",
        "subagent_stopped_count": "⏹ [SubagentManager] Stopped {count} running tasks.",
        
        "cron_load_fail": "⚠️ [Cron] Load failed: {e}",
        "cron_starting": "⏰ [Cron] Service started with {count} tasks.",
        "cron_skipping": "⏭️ [Cron] Task still running, skipping re-entry: {name} ({id})",
        "cron_triggering": "⚡️ [Cron] Triggering task: {name} ({id})",
        "cron_fail": "❌ [Cron] Task execution failed: {e}",
        "cron_removed": "🚫 [Cron] Forcibly stopped and removed task: {id}",
        "cron_cancelled": "🚫 [Cron] Cancelled running task: {id}",
        "cron_cleared": "🧹 [Cron] Cleared all tasks ({count} in total)"
    }
}

i18n = STRINGS.get(BOT_LANGUAGE, STRINGS["en"])
