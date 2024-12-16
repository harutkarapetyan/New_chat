from fastapi import  WebSocket, HTTPException, status, APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from models.models import User
from database import get_db

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from core import security

# from app.core.security import get_current_user

# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
#
#
# template = Jinja2Templates(directory="templates")

chat_router = APIRouter(tags=["chat"], prefix="/api/chat")

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name='static')


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


@chat_router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, db: Session = Depends(get_db),
                         token = str):

    await manager.connect(websocket)

    try:
        user = security.get_current_user(token, db)

        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{user.first_name} {user.last_name} ->: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user disconnected.")
