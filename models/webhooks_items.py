from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    DECIMAL,
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


class WebhookItem(Base):
    __tablename__ = "webhook_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    webhook_id: Mapped[int] = mapped_column(Integer, ForeignKey(""), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey(""), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    


    