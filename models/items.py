from sqlalchemy import (
    ForeignKey, 
    Integer, 
    String, 
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import Base


class Items(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    zoho_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    ecwid_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    store_id: Mapped[int] = mapped_column(Integer, ForeignKey("stores.id"), nullable=False)


    