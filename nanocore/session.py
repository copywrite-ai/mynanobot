import json
from pathlib import Path
from typing import Any
from .logger import logger

class SessionManager:
    """管理会话历史的持久化存储。"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"💾 [Session] 会话存储目录: {self.storage_dir}")

    def _get_path(self, session_key: str) -> Path:
        # 移除非法字符，防止路径穿越
        safe_key = "".join([c for c in session_key if c.isalnum() or c in ("-", "_")]).strip()
        return self.storage_dir / f"{safe_key}.json"

    def load(self, session_key: str) -> list[dict[str, Any]]:
        """加载指定会话的历史记录。"""
        path = self._get_path(session_key)
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"❌ [Session] 加载会话 {session_key} 失败: {e}")
            return []

    def save(self, session_key: str, messages: list[dict[str, Any]]):
        """持久化保存会话历史记录。"""
        path = self._get_path(session_key)
        try:
            path.write_text(json.dumps(messages, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"❌ [Session] 保存会话 {session_key} 失败: {e}")

    def list_sessions(self) -> list[str]:
        """列出所有已存在的会话。"""
        return [f.stem for f in self.storage_dir.glob("*.json")]

    def delete(self, session_key: str):
        """删除会话及其历史记录。"""
        path = self._get_path(session_key)
        if path.exists():
            path.unlink()
            logger.info(f"🗑️ [Session] 已删除会话: {session_key}")
