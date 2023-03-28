import bcrypt

from sqlalchemy import Boolean, Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(255), nullable=False, unique=True)
    password = Column(String, nullable=False)
    active = Column(Boolean, default=False)
    messages = relationship("Message", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, active={self.active})>"

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_bot = Column(Boolean, default=False)
    user = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, user_id={self.user_id}, text={self.text}, is_bot={self.is_bot}, timestamp={self.timestamp})>"
