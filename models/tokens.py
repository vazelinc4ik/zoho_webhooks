
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

class ZohoTokens(Base):
    __tablename__ = "zoho_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, unique=True)
    store_id: Mapped[int] = mapped_column(Integer, ForeignKey("stores.id"), nullable=False, unique=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    expires_in: Mapped[int] = mapped_column(BigInteger, nullable=False)