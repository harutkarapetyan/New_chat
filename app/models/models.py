import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, text, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    status = Column(Boolean, nullable=True, server_default="False")
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))


class ResetPassword(Base):
    __tablename__ = "password_reset"

    password_resset_id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    code = Column(Integer, nullable=False, unique=True)


class Message(Base):
    __tablename__ = "message"

    message_id = Column(Integer, nullable=False, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # Group chats might not need receiver
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False)


    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    # parent_message = relationship("Message", remote_side=[message_id])



    # chat_room_id = Column(Integer, ForeignKey("chat_room.chat_room_id"), nullable=True)
    # message_type = Column(String, default="text", nullable=False)
    # attachments = Column(String, nullable=True)
    # edited = Column(Boolean, default=False)
    # parent_message_id = Column(Integer, ForeignKey("message.message_id"), nullable=True)
