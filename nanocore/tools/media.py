import asyncio
from .base import BaseTool
from nanocore.logger import logger

class MediaTool(BaseTool):
    """智能控制 macOS 全局媒体（比纯模拟按键更稳定）。"""
    name = "media_control"
    description = "Control system-wide media playback. Supports play/pause, next, previous, and volume control. Works globally regardless of window focus."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["play_pause", "next", "previous", "volume_up", "volume_down", "mute", "status"],
                "description": "The action: play_pause (toggle), next, previous, volume_up, volume_down, mute, or status."
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str) -> str:
        if action == "play_pause":
            # 优先检查网易云音乐，因为用户明确要求使用该指令
            script = """
            try
                if application "NeteaseMusic" is running then
                    tell application "NeteaseMusic" to activate
                    delay 0.2
                    tell application "System Events" to keystroke " "
                    return "NeteaseMusic: Play/Pause toggled via Space"
                else
                    error "NeteaseMusic not running"
                end if
            on error
                try
                    tell application "Music" to playpause
                    return "Music.app: playpause sent"
                on error
                    try
                        tell application "Spotify" to playpause
                        return "Spotify: playpause sent"
                    on error
                        # 最后的保底手段：发送全局硬件媒体键信号 (F8)
                        tell application "System Events" to key code 101
                        return "System: F8 (Media Key) sent"
                    end try
                end try
            end try
            """
        elif action == "next":
            script = """
            try
                if application "Music" is running then
                    tell application "Music" to next track
                else
                    tell application "System Events" to key code 103
                end if
            on error
                tell application "System Events" to key code 103
            end try
            """
        elif action == "previous":
            script = """
            try
                if application "Music" is running then
                    tell application "Music" to previous track
                else
                    tell application "System Events" to key code 100
                end if
            on error
                tell application "System Events" to key code 100
            end try
            """
        elif action == "volume_up":
            script = "set volume output volume ((output volume of (get volume settings)) + 10)"
        elif action == "volume_down":
            script = "set volume output volume ((output volume of (get volume settings)) - 10)"
        elif action == "mute":
            script = "set volume with output muted"
        elif action == "status":
            script = """
            if application "Music" is running then
                tell application "Music"
                    if player state is playing then
                        return "Music.app 正在播放: " & name of current track & " - " & artist of current track
                    else
                        return "Music.app 已暂停"
                    end if
                end tell
            else
                return "Music.app 未运行"
            end if
            """
        else:
            return f"Error: Unsupported action '{action}'"

        return await self._run_osascript(script)

    async def _run_osascript(self, script: str) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                "osascript", "-e", script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                err_msg = stderr.decode().strip()
                logger.error(f"MediaTool Error: {err_msg}")
                return f"Error: {err_msg}"
            res = stdout.decode().strip()
            return res if res else "Command executed successfully"
        except Exception as e:
            return f"Exception: {str(e)}"
