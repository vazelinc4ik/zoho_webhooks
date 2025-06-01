

from typing import Generic, TypeVar, Type, ClassVar, Any

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core import async_session_maker

from models import (
    Items,
    Orders,
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
    async def patch_entity(cls, db: AsyncSession, entity: M, **data: Any) -> M:
        if not data:
            raise ValueError("No data provided for update")
        
        if not hasattr(entity, "id") or entity.id is None:
            raise ValueError("Entity must have an ID to be updated")
        
        stmt = (
            update(cls.model)
            .where(cls.model.id == entity.id)
            .values(**data)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(entity)
        return entity

    @classmethod
    async def create_entity(cls, db: AsyncSession, **data: Any) -> M:
        if not data:
            raise ValueError("No data provided for create")
            
        query = insert(cls.model).values(**data).returning(cls.model)
        result = await db.execute(query)
        entity = result.scalar_one()
        await db.commit()

        return entity
    
        
class ItemsCRUD(BaseCRUD[Items]):
    model = Items

class StoresCRUD(BaseCRUD[Stores]):
    model = Stores

class OrdersCRUD(BaseCRUD[Orders]):
    model = Orders

class ZohoTokensCRUD(BaseCRUD[ZohoTokens]):
    model = ZohoTokens

    @classmethod
    async def find_and_patch(
        cls,
        db: AsyncSession,
        zoho_organization_id: int,
        access_token: str,
        refresh_token: str,
        expires
    ) -> None:
        old_entity = await cls.find_one_or_none(db, zoho_organization_id=zoho_organization_id)

        if old_entity:
            await cls.patch_entity(db, old_entity, access_token=access_token, refresh_token=refresh_token)
            return
        
        await cls.create_entity(db, access_token=access_token, refresh_token=refresh_token)



