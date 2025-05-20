

from typing import Generic, TypeVar, Type, ClassVar, Any

from sqlalchemy import select

from core import async_session_maker

from models import (
    Items,
    Stores
)

M = TypeVar('M')

class BaseCRUD(Generic[M]):
    model: ClassVar[Type[M]]

    @classmethod
    async def find_one_or_none(cls, **data: Any) -> M:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**data)
            result = await session.execute(query)
            return result.scalars().one_or_none()
        
class ItemsCRUD(BaseCRUD[Items]):
    model = Items


class StoresCRUD(BaseCRUD[Stores]):
    model = Stores