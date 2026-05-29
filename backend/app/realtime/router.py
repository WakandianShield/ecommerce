from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from jose import JWTError

from app.application.use_cases.chat_service import ChatService
from app.domain.entities.chat import ChatMessage
from app.adapters.api.dependencies import require_roles
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.repositories import SqlAlchemyChatRepository
from app.infrastructure.realtime.in_memory_faq_repository import InMemoryFaqRepository
from app.infrastructure.realtime.simple_faq_matcher import SimpleFaqMatcher
from app.infrastructure.security.token_service import TokenService
from app.realtime.connection_manager import ConnectionManager


router = APIRouter(prefix="/realtime", tags=["realtime"])

_manager = ConnectionManager()
_faq_repository = InMemoryFaqRepository()
_faq_matcher = SimpleFaqMatcher()


def _chat_service(db) -> ChatService:
    return ChatService(SqlAlchemyChatRepository(db), _faq_repository, _faq_matcher)


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
    with SessionLocal() as db:
        return {"sessions": _chat_service(db).list_sessions()}


@router.get("/sessions/{session_id}")
def get_session_messages(session_id: str, profile=Depends(require_roles("admin", "operator"))):
    with SessionLocal() as db:
        messages = _chat_service(db).list_messages(session_id)
    return {
        "session_id": session_id,
        "messages": [_serialize_message(message) for message in messages],
    }


class AdminReplyBody(BaseModel):
    content: str


@router.post("/sessions/{session_id}/reply")
async def admin_reply(
    session_id: str,
    body: AdminReplyBody,
    _profile=Depends(require_roles("admin", "operator")),
):
    try:
        with SessionLocal() as db:
            message = _chat_service(db).inject_assistant_message(session_id, body.content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await _manager.broadcast_json(
        session_id,
        {"type": "message", "message": _serialize_message(message)},
    )
    return {"message": _serialize_message(message)}


@router.websocket("/chat")
async def chat_socket(websocket: WebSocket):
    session_id = websocket.query_params.get("session_id")
    db = SessionLocal()
    service = _chat_service(db)
    session_id = service.open_session(session_id)
    await _manager.connect(websocket, session_id)
    await websocket.send_json({"type": "session", "session_id": session_id})
    await websocket.send_json(
        {
            "type": "history",
            "messages": [_serialize_message(message) for message in service.list_messages(session_id)],
        }
    )
    await _manager.broadcast_admin_json({"type": "sessions", "sessions": service.list_sessions()})
    try:
        while True:
            text = await websocket.receive_text()
            try:
                user_message, assistant_message = service.handle_message(session_id, text)
            except ValueError:
                await websocket.send_json({"type": "error", "message": "Empty message"})
                continue
            await _manager.broadcast_json(
                session_id,
                {"type": "message", "message": _serialize_message(user_message)},
            )
            await _manager.broadcast_json(
                session_id,
                {"type": "message", "message": _serialize_message(assistant_message)},
            )
            await _manager.broadcast_admin_json({"type": "sessions", "sessions": service.list_sessions()})
    except WebSocketDisconnect:
        _manager.disconnect(session_id, websocket)
    finally:
        db.close()


@router.websocket("/admin/chat")
async def admin_chat_socket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    session_id = websocket.query_params.get("session_id")
    if not token or not session_id:
        await websocket.close(code=1008)
        return
    try:
        payload = TokenService().decode_token(token)
    except JWTError:
        await websocket.close(code=1008)
        return
    if payload.get("type") != "access" or payload.get("role") not in {"admin", "operator"}:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    service = _chat_service(db)
    service.open_session(session_id)
    await _manager.connect(websocket, session_id)
    try:
        await websocket.send_json(
            {
                "type": "history",
                "messages": [_serialize_message(message) for message in service.list_messages(session_id)],
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _manager.disconnect(session_id, websocket)
    finally:
        db.close()


@router.websocket("/admin/sessions")
async def admin_sessions_socket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        payload = TokenService().decode_token(token)
    except JWTError:
        await websocket.close(code=1008)
        return
    if payload.get("type") != "access" or payload.get("role") not in {"admin", "operator"}:
        await websocket.close(code=1008)
        return

    with SessionLocal() as db:
        sessions = _chat_service(db).list_sessions()
    await _manager.connect_admin(websocket)
    await websocket.send_json({"type": "sessions", "sessions": sessions})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _manager.disconnect_admin(websocket)
