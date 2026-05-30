from collections import defaultdict
from threading import Lock
from typing import List

from app.domain.entities.chat import ChatMessage, ChatSession


class InMemoryChatRepository:
    def __init__(self) -> None:
        self._messages = defaultdict(list)
        self._sessions: dict[str, ChatSession] = {}
        self._lock = Lock()

    def create_session(
        self,
        session_id: str,
        customer_name: str | None = None,
        profile_id: str | None = None,
    ) -> None:
        with self._lock:
            self._messages.setdefault(session_id, [])
            self._sessions[session_id] = ChatSession(
                id=session_id,
                customer_name=customer_name,
                profile_id=profile_id,
            )

    def get_session_for_profile(self, profile_id: str, customer_name: str | None = None) -> ChatSession | None:
        with self._lock:
            for session in self._sessions.values():
                if session.profile_id == profile_id:
                    return session
        return None

    def list_sessions(self) -> List[ChatSession]:
        with self._lock:
            return [
                self._sessions.get(session_id, ChatSession(id=session_id, customer_name=None))
                for session_id in self._messages.keys()
            ]

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        with self._lock:
            self._messages.setdefault(session_id, []).append(message)

    def list_messages(self, session_id: str) -> List[ChatMessage]:
        with self._lock:
            return list(self._messages.get(session_id, []))
