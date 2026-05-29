from dataclasses import dataclass
from datetime import datetime


SENDER_CUSTOMER = "customer"
SENDER_ASSISTANT = "assistant"
SENDER_ADMIN = "admin"


@dataclass(frozen=True)
class ChatMessage:
    id: str
    session_id: str
    sender: str
    content: str
    created_at: datetime
