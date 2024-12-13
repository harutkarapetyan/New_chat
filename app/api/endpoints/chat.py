# from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy.orm import Session
# from models import User, Message, Base
# from database import SessionLocal
#
# app = FastAPI()
#
# # send message
# @app.post("/send_message/")
# def send_message(
#     sender_id: int,
#     receiver_id: int = None,  #, if ID NULL -> global
#     content: str,
#     db: Session = Depends(SessionLocal)
# ):
#     if receiver_id is None:
#         users = db.query(User).all()
#         for user in users:
#             message = Message(
#                 sender_id=sender_id,
#                 receiver_id=user.user_id,
#                 content=content
#             )
#             db.add(message)
#         db.commit()
#         return {"message": "Global message sent to all users"}
#     else:
#         # for special user
#         message = Message(
#             sender_id=sender_id,
#             receiver_id=receiver_id,
#             content=content
#         )
#         db.add(message)
#         db.commit()
#         return {"message": f"Message sent to user {receiver_id}"}
#
#
#


from fastapi import  WebSocket, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from models.models import User, Message
from database import SessionLocal, get_db

chat_router = APIRouter(tags=["chat"], prefix="/api/chat")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    def connect(self, websocket: WebSocket, user_id: int):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    def send_message(self, user_id: int, message: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                connection.send_text(message)

    def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for connection in connections:
                connection.send_text(message)

manager = ConnectionManager()

@chat_router.websocket("/ws/{user_id}")
def websocket_endpoint(websocket: WebSocket, user_id: int):
    db = SessionLocal()
    manager.connect(websocket, user_id)
    try:
        while True:
            data = websocket.receive_text()
            # Assuming data is in the format: "receiver_id:message"
            if ":" in data:
                receiver_id, content = data.split(":", 1)
                receiver_id = int(receiver_id)
                if receiver_id == 0:
                    # Global message
                    manager.broadcast(content)
                    users = db.query(User).all()
                    for user in users:
                        message = Message(sender_id=user_id, receiver_id=user.user_id, content=content)
                        db.add(message)
                else:
                    # Specific user message
                    manager.send_message(receiver_id, content)
                    message = Message(sender_id=user_id, receiver_id=receiver_id, content=content)
                    db.add(message)
                db.commit()
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message": str(error)})
    finally:
        manager.disconnect(websocket, user_id)
        db.close()


