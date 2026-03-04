import json
import os
from pathlib import Path
from .logger import logger

class SessionManager:
    """负责对话会话的持久化管理。"""
    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, session_id: str) -> Path:
        return self.storage_dir / f"{session_id}.json"

    def load(self, session_id: str) -> list[dict]:
        """加载指定会话的历史消息。"""
        path = self._get_path(session_id)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"⚠️ 加载会话 {session_id} 失败: {e}")
        return []

    def save(self, session_id: str, messages: list[dict]):
        """保存当前会话的消息列表。"""
        path = self._get_path(session_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"⚠️ 保存会话 {session_id} 失败: {e}")
