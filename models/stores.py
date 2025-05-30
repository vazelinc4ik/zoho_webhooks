
from sqlalchemy import (
    BigInteger,
    Integer,
    String
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import Base


class Stores(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)

    #Отдается зохо в хэдерах
    zoho_organization_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    #Отдается эквидом при вебхуках
    ecwid_store_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    
    location: Mapped[str] = mapped_column(String, nullable=False, server_default="eu")



    