from datetime import datetime, timezone
import uuid

from app.domain.entities.chat import ChatMessage, SENDER_ASSISTANT, SENDER_CUSTOMER
from app.domain.ports.chat_repository import ChatRepository
from app.domain.ports.faq_matcher import FaqMatcher
from app.domain.ports.faq_repository import FaqRepository


class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        faq_repo: FaqRepository,
        faq_matcher: FaqMatcher,
    ) -> None:
        self._chat_repo = chat_repo
        self._faq_repo = faq_repo
        self._faq_matcher = faq_matcher

    def open_session(self, session_id: str | None = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())
        self._chat_repo.create_session(session_id)
        return session_id

    def handle_message(self, session_id: str, text: str) -> tuple[ChatMessage, ChatMessage]:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Empty message")
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sender=SENDER_CUSTOMER,
            content=cleaned,
            created_at=datetime.now(timezone.utc),
        )
        self._chat_repo.add_message(session_id, user_message)
        response_text = self._build_response(cleaned)
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sender=SENDER_ASSISTANT,
            content=response_text,
            created_at=datetime.now(timezone.utc),
        )
        self._chat_repo.add_message(session_id, assistant_message)
        return user_message, assistant_message

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        return self._chat_repo.list_messages(session_id)

    def list_sessions(self) -> list[str]:
        return self._chat_repo.list_sessions()

    def _build_response(self, text: str) -> str:
        entries = self._faq_repo.list_entries()
        match = self._faq_matcher.match(text, entries)
        if match:
            return match.answer
        return "No tengo una respuesta automatica. Un asistente te contactara pronto."
