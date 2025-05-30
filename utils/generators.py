from typing import AsyncGenerator, Generator

from ecwid_api import EcwidApi
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core import async_session_maker
from crud import StoresCRUD

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_ecwid_api(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> EcwidApi:
    zoho_organization_id = request.headers.get("x-com-zoho-organizationid")
    if not zoho_organization_id:
        raise HTTPException(status_code=400, detail="Missing organization ID header")
    try:
        store = await StoresCRUD.find_one_or_none(db, zoho_organization_id=zoho_organization_id)
    except Exception as e:
        print(f'Failed to find store {e}')
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return EcwidApi(store.ecwid_store_id, settings.ecwid_settings.ecwid_app_secret)