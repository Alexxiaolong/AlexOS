from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    whatsapp_message_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    sender_phone: Mapped[str] = mapped_column(String(32), index=True)
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    items: Mapped[list["Item"]] = relationship(back_populates="source_message")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), index=True)

    folder: Mapped[str] = mapped_column(String(120), default="Da classificare")
    item_type: Mapped[str] = mapped_column(String(40), default="nota")
    title: Mapped[str] = mapped_column(String(300))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="media")
    status: Mapped[str] = mapped_column(String(30), default="aperto")
    due_at: Mapped[str | None] = mapped_column(String(80), nullable=True)
    waiting_for: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calendar_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    source_message: Mapped[Message] = relationship(back_populates="items")
