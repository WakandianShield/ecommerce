from collections import defaultdict
from threading import Lock
from typing import List

from app.domain.entities.chat import ChatMessage, ChatSession


class InMemoryChatRepository:
    def __init__(self) -> None:
        self._messages = defaultdict(list)
        self._lock = Lock()

    def create_session(self, session_id: str, customer_name: str | None = None) -> None:
        with self._lock:
            self._messages.setdefault(session_id, [])

    def list_sessions(self) -> List[ChatSession]:
        with self._lock:
            return [ChatSession(id=session_id, customer_name=None) for session_id in self._messages.keys()]

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        with self._lock:
            self._messages.setdefault(session_id, []).append(message)

    def list_messages(self, session_id: str) -> List[ChatMessage]:
        with self._lock:
            return list(self._messages.get(session_id, []))
