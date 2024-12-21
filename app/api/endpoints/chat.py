import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from models.models import User, MessageGlobal, OneToOneMessage
from database import get_db
from core import security

chat_router = APIRouter(tags=["chat"], prefix="/api/chat")


# Manage connected WebSocket clients and active users
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.active_users: dict[int, User] = {}  # user_id mapped to User object

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_users[user.user_id] = user

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove(websocket)
        if user_id in self.active_users:
            del self.active_users[user_id]

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@chat_router.websocket("/global/chat")
async def global_chat_websocket(websocket: WebSocket, db: Session = Depends(get_db), token = str):
    try:
        user = security.get_current_user(token, db)
        await manager.connect(websocket, user)

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
                await websocket.send_text("Error: Message not saved to database.")
                print(f"Error saving message: {e}")
                continue

            timestamp = message.timestamp.strftime('%d %b %H:%M')

            await manager.broadcast(f"{user.first_name} {user.last_name} {timestamp} -> {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.user_id)
        await manager.broadcast("A user disconnected.")


@chat_router.websocket("/one-to-one/chat/{receiver_id}")
async def one_to_one_chat_websocket(
    websocket: WebSocket,
    receiver_id: int,
    db: Session = Depends(get_db),
    token = str
):
    try:
        sender = security.get_current_user(token, db)
        print(f"sender: {sender}")
        await manager.connect(websocket, sender)

        # Verify that the recipient exists
        receiver = db.query(User).filter(User.user_id == receiver_id).first()

        if not receiver:
            await websocket.send_text("Error: Receiver does not exist.")
            return

        while True:
            data = await websocket.receive_text()
            if data is None:
                time.sleep(3)
                continue

            # Save data to database
            message = OneToOneMessage(
                sender_id=sender.user_id,
                receiver_id=receiver.user_id,
                content=data,
            )
            try:
                db.add(message)
                db.commit()
                db.refresh(message)
            except Exception as e:
                db.rollback()
                await websocket.send_text("Error: Message not saved to database.")
                print(f"Error saving message: {e}")
                continue

            timestamp = message.timestamp.strftime('%d %b %H:%M')

            #Send the message to the sender and recipient
            for connection in manager.active_connections:
                await connection.send_text(f"{sender.first_name} {sender.last_name} {timestamp} -> {data}")
    except WebSocketDisconnect:
        pass
        manager.disconnect(websocket, sender.user_id)
        await manager.broadcast(f"A user disconnected.")



