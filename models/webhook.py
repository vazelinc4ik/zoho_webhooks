from datetime import datetime, timezone
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Identity, 
    Integer, 
    String, 
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


    