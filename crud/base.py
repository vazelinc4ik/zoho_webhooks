

from typing import Generic, TypeVar, Type, ClassVar, Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core import async_session_maker

from models import (
    Items,
    Stores,
    ZohoTokens
)

M = TypeVar('M')

class BaseCRUD(Generic[M]):
    model: ClassVar[Type[M]]

    @classmethod
    async def find_one_or_none(cls, db: AsyncSession, **data: Any) -> M:
        stmt = select(cls.model).filter_by(**data)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()
        
    @classmethod
    async def patch_entity(cls, entity: M, **data: Any) -> M:
        async with async_session_maker() as session:
            if not data:
                raise ValueError("No data provided for update")
            
            if not hasattr(entity, "id") or entity.id is None:
                raise ValueError("Entity must have an ID to be updated")
            
            stmt = (
                update(cls)
                .where(cls.id == entity.id)
                .values(**data)
            )

            await session.execute(stmt)
            await session.commit()

            await session.refresh(entity)

            return entity

    @classmethod
    async def create_entity(cls, **data: Any) -> M:
        async with async_session_maker() as session:
            if not data:
                raise ValueError("No data provided for update")
            
            entity = cls(**data)
            session.add(entity)
            await session.commit()
            await session.refresh(entity)

            return entity
    
        
class ItemsCRUD(BaseCRUD[Items]):
    model = Items

class StoresCRUD(BaseCRUD[Stores]):
    model = Stores

class ZohoTokensCRUD(BaseCRUD[ZohoTokens]):
    model = ZohoTokens

    @classmethod
    async def find_and_patch(
        cls,
        zoho_organization_id: int,
        access_token: str,
        refresh_token: str,
    ) -> None:
        old_entity = await cls.find_one_or_none(zoho_organization_id=zoho_organization_id)
        if old_entity:
            await cls.patch_entity(old_entity, access_token=access_token, refresh_token=refresh_token)
            return
        await cls.create_entity(access_token=access_token, refresh_token=refresh_token)



