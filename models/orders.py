from sqlalchemy import (
    BigInteger,
    ForeignKey, 
    Integer, 
    String, 
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import Base


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    zoho_order_id: Mapped[str] = mapped_column(String, nullable=False)
    ecwid_order_id: Mapped[str] = mapped_column(String, nullable=False)
    store_id: Mapped[int] = mapped_column(Integer, ForeignKey("stores.id"), nullable=False)

