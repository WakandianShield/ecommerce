from typing import List, Protocol

from app.domain.entities.chat import ChatMessage, ChatSession


class ChatRepository(Protocol):
    def create_session(self, session_id: str, customer_name: str | None = None) -> None:
        ...

    def list_sessions(self) -> List[ChatSession]:
        ...

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        ...

    def list_messages(self, session_id: str) -> List[ChatMessage]:
        ...
