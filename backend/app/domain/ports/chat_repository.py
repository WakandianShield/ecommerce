from typing import List, Protocol

from app.domain.entities.chat import ChatMessage


class ChatRepository(Protocol):
    def create_session(self, session_id: str) -> None:
        ...

    def list_sessions(self) -> List[str]:
        ...

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        ...

    def list_messages(self, session_id: str) -> List[ChatMessage]:
        ...
