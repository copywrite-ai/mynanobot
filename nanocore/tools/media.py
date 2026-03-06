import asyncio
from .base import BaseTool
from nanocore.logger import logger

class MediaTool(BaseTool):
    """智能控制 macOS 全局媒体（支持特定应用控制及全局热键）。"""
    name = "media_control"
    description = "Control system-wide media playback. Supports play/pause, next, previous, volume, position, and metadata retrieval. Enhanced Spotify support."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "play_pause", "next", "previous", "volume_up", "volume_down", "mute", 
                    "status", "set_volume", "set_position", "get_info", "set_shuffle", "set_repeat"
                ],
                "description": "The action to perform."
            },
            "app_name": {
                "type": "string",
                "description": "Optional: 'Spotify', 'NeteaseMusic', or 'Music'."
            },
            "value": {
                "type": "string",
                "description": "Optional: Value for the action (e.g., volume 0-100, position in seconds, 'on'/'off' for shuffle/repeat)."
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, app_name: str = None, value: str = None) -> str:
        if action == "play_pause":
            if app_name == "NeteaseMusic":
                script = 'tell application "System Events" to keystroke " " using {control down, option down}'
                return await self._run_osascript(script) + " (NeteaseMusic shortcut)"
            elif app_name:
                script = f'tell application "{app_name}" to playpause'
                return await self._run_osascript(script)
            else:
                # 默认优先级逻辑
                script = """
                try
                    if application "NeteaseMusic" is running then
                        tell application "System Events" to keystroke " " using {control down, option down}
                        return "NeteaseMusic: toggled via Control+Option+Space"
                    else if application "Spotify" is running then
                        tell application "Spotify" to playpause
                        return "Spotify: playpause sent"
                    else if application "Music" is running then
                        tell application "Music" to playpause
                        return "Music.app: playpause sent"
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
        elif action == "set_volume":
            vol = value if value else "50"
            if app_name == "Spotify":
                script = f'tell application "Spotify" to set sound volume to {vol}'
            else:
                script = f"set volume output volume {vol}"
        elif action == "set_position":
            pos = value if value else "0"
            if app_name == "Spotify":
                script = f'tell application "Spotify" to set player position to {pos}'
            else:
                return "Error: set_position is currently only supported for Spotify"
        elif action == "get_info" or action == "status":
            if app_name == "Spotify" or (not app_name and await self._is_running("Spotify")):
                script = """
                tell application "Spotify"
                    set trackName to name of current track
                    set trackArtist to artist of current track
                    set trackAlbum to album of current track
                    set trackUrl to spotify url of current track
                    set pState to player state as string
                    return "Spotify (" & pState & "): " & trackName & " - " & trackArtist & " [" & trackAlbum & "] URL: " & trackUrl
                end tell
                """
            elif app_name == "Music" or (not app_name and await self._is_running("Music")):
                script = """
                tell application "Music"
                    if player state is playing then
                        return "Music.app 正在播放: " & name of current track & " - " & artist of current track
                    else
                        return "Music.app 已暂停"
                    end if
                end tell
                """
            else:
                return "No supported music app running or specified for info"
        elif action == "set_shuffle":
            mode = "true" if value in ["on", "true", "yes"] else "false"
            if app_name == "Spotify":
                script = f'tell application "Spotify" to set shuffling to {mode}'
            else:
                return "Error: set_shuffle is only supported for Spotify"
        elif action == "set_repeat":
            mode = "true" if value in ["on", "true", "yes"] else "false"
            if app_name == "Spotify":
                script = f'tell application "Spotify" to set repeating to {mode}'
            else:
                return "Error: set_repeat is only supported for Spotify"
        elif action == "mute":
            script = "set volume with output muted"
        else:
            return f"Error: Unsupported action '{action}'"

        return await self._run_osascript(script)

    async def _is_running(self, app_name: str) -> bool:
        script = f'application "{app_name}" is running'
        res = await self._run_osascript(script)
        return res == "true"

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
