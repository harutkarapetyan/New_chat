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


class MessageGlobal(Base):
    __tablename__ = "global_message"

    message_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # is_read = Column(Boolean, default=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])


class OneToOneMessage(Base):
    __tablename__ = "one_to_one_message"

    message_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # is_read = Column(Boolean, default=False, nullable=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")