from typing import AsyncGenerator, Generator

from ecwid_api import EcwidApi
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core import async_session_maker
from crud import StoresCRUD

async def get_ecwid_api(request: Request) -> AsyncGenerator[EcwidApi, None]:
    zoho_organization_id = 20106177882
    if not zoho_organization_id:
        raise HTTPException(status_code=400, detail="Missing organization ID header")
    store = await StoresCRUD.find_one_or_none(zoho_organization_id=zoho_organization_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    yield EcwidApi(store.ecwid_store_id, settings.ecwid_settings.ecwid_app_secret)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session