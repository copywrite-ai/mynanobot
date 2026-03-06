import asyncio
from .base import BaseTool
from nanocore.logger import logger

class MediaTool(BaseTool):
    """智能控制 macOS 全局媒体（支持特定应用控制及全局热键）。"""
    name = "media_control"
    description = "Control system-wide media playback. Supports play/pause, next, previous, and volume control. Can target specific apps like 'Spotify', 'NeteaseMusic', or 'Music'."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["play_pause", "next", "previous", "volume_up", "volume_down", "mute", "status"],
                "description": "The action: play_pause (toggle), next, previous, volume_up, volume_down, mute, or status."
            },
            "app_name": {
                "type": "string",
                "description": "Optional: Specific application to target (e.g., 'Spotify', 'NeteaseMusic', 'Music')."
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, app_name: str = None) -> str:
        if action == "play_pause":
            if app_name:
                # 明确指定了应用，直接发送后台指令
                script = f'tell application "{app_name}" to playpause'
            else:
                # 默认优先级逻辑
                script = """
                try
                    if application "Spotify" is running then
                        tell application "Spotify" to playpause
                        return "Spotify: playpause sent"
                    else if application "Music" is running then
                        tell application "Music" to playpause
                        return "Music.app: playpause sent"
                    else if application "NeteaseMusic" is running then
                        tell application "NeteaseMusic" to playpause
                        return "NeteaseMusic: playpause sent"
                    else
                        error "No known music application running"
                    end if
                on error
                    # 最后的保底手段：发送全局硬件媒体键信号 (F8 = 101)
                    tell application "System Events" to key code 101
                    return "System: F8 (Media Key) sent as fallback"
                end try
                """
        elif action == "next":
            if app_name:
                script = f'tell application "{app_name}" to next track'
            else:
                script = """
                try
                    if application "Spotify" is running then
                        tell application "Spotify" to next track
                    else if application "Music" is running then
                        tell application "Music" to next track
                    else
                        tell application "System Events" to key code 103
                    end if
                on error
                    tell application "System Events" to key code 103
                end try
                """
        elif action == "previous":
            if app_name:
                script = f'tell application "{app_name}" to previous track'
            else:
                script = """
                try
                    if application "Spotify" is running then
                        tell application "Spotify" to previous track
                    else if application "Music" is running then
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
            else if application "Spotify" is running then
                 tell application "Spotify"
                    if player state is playing then
                        return "Spotify 正在播放: " & name of current track & " - " & artist of current track
                    else
                        return "Spotify 已暂停"
                    end if
                end tell
            else
                return "No supported music app running for status check"
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
