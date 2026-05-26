from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.application.use_cases.chat_service import ChatService
from app.domain.entities.chat import ChatMessage
from app.adapters.api.dependencies import require_roles
from app.infrastructure.realtime.in_memory_chat_repository import InMemoryChatRepository
from app.infrastructure.realtime.in_memory_faq_repository import InMemoryFaqRepository
from app.infrastructure.realtime.simple_faq_matcher import SimpleFaqMatcher
from app.realtime.connection_manager import ConnectionManager


router = APIRouter(prefix="/realtime", tags=["realtime"])

_manager = ConnectionManager()
_chat_service = ChatService(
    InMemoryChatRepository(),
    InMemoryFaqRepository(),
    SimpleFaqMatcher(),
)


def _serialize_message(message: ChatMessage) -> dict:
    return {
        "id": message.id,
        "session_id": message.session_id,
        "sender": message.sender,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


@router.get("/sessions")
def list_sessions(profile=Depends(require_roles("admin", "operator"))):
    return {"sessions": _chat_service.list_sessions()}


@router.get("/sessions/{session_id}")
def get_session_messages(session_id: str, profile=Depends(require_roles("admin", "operator"))):
    messages = _chat_service.list_messages(session_id)
    return {
        "session_id": session_id,
        "messages": [_serialize_message(message) for message in messages],
    }


@router.websocket("/chat")
async def chat_socket(websocket: WebSocket):
    session_id = websocket.query_params.get("session_id")
    session_id = _chat_service.open_session(session_id)
    await _manager.connect(websocket, session_id)
    await _manager.send_json(session_id, {"type": "session", "session_id": session_id})
    try:
        while True:
            text = await websocket.receive_text()
            try:
                user_message, assistant_message = _chat_service.handle_message(session_id, text)
            except ValueError:
                await _manager.send_json(session_id, {"type": "error", "message": "Empty message"})
                continue
            await _manager.send_json(
                session_id,
                {"type": "message", "message": _serialize_message(user_message)},
            )
            await _manager.send_json(
                session_id,
                {"type": "message", "message": _serialize_message(assistant_message)},
            )
    except WebSocketDisconnect:
        _manager.disconnect(session_id)
