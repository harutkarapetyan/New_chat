from fastapi import  WebSocket, HTTPException, status, APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from models.models import User, MessageGlobal
from database import get_db

from fastapi import WebSocket, WebSocketDisconnect, Request
from core import security

chat_router = APIRouter(tags=["chat"], prefix="/api/chat")


# Manage connected WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@chat_router.websocket("/global/chat")
async def global_chat_websocket(websocket: WebSocket, db: Session = Depends(get_db), token = str):
    await manager.connect(websocket)

    try:
        user = security.get_current_user(token, db)

        while True:
            data = await websocket.receive_text()

            message = MessageGlobal(
                sender_id=user.user_id,
                content=data,
            )
            try:
                db.add(message)
                db.commit()
                db.refresh(message)
            except Exception as e:
                db.rollback()
                await websocket.send_text("❌ Error: Message not saved to database.")
                print(f"Error saving message: {e}")
                continue

            timestamp = message.timestamp.strftime('%d %b %H:%M')


            await manager.broadcast(f"{user.first_name} {user.last_name} {timestamp} -> {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user disconnected.")
