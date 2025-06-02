import httpx

from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Generator

from ecwid_api import EcwidApi
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from zoho_api import ZohoApi

from core.config import settings
from core import async_session_maker
from crud import StoresCRUD, ZohoTokensCRUD
from .security.auth import generate_zoho_refresh_url


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# async def get_ecwid_api(
#     request: Request,
#     db: AsyncSession = Depends(get_db)
# ) -> EcwidApi:

#     zoho_organization_id = request.headers.get("x-com-zoho-organizationid")
#     if not zoho_organization_id:
#         raise HTTPException(status_code=400, detail="Missing organization ID header")
    
#     store = await StoresCRUD.find_one_or_none(db, zoho_organization_id=zoho_organization_id)
#     if not store:
#         raise HTTPException(status_code=404, detail="Store not found")

#     return EcwidApi(store.ecwid_store_id, settings.ecwid_settings.ecwid_app_secret)

async def get_ecwid_api(
) -> EcwidApi:
    return EcwidApi(settings.ecwid_settings.ecwid_store_id, settings.ecwid_settings.ecwid_app_secret)

async def get_zoho_api(
    data: Dict[str, Any],
    db: AsyncSession
) -> ZohoApi:
    try:
        ecwid_store_id = data.get('storeId')
        store = await StoresCRUD.find_one_or_none(db, ecwid_store_id=ecwid_store_id)

        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
            
        tokens = await ZohoTokensCRUD.find_one_or_none(db, store_id=store.id)
        if tokens.expires_in - 60 < datetime.now().timestamp():
            url = generate_zoho_refresh_url(tokens.refresh_token)
            async with httpx.AsyncClient() as client:
                response = await client.post(url)
            payload = response.json()
            data = {
                "access_token": payload.get('access_token'),
                "expires_in": datetime.now().timestamp() + payload.get('expires_in')
            }
            tokens = await ZohoTokensCRUD.patch_entity(db, tokens, **data)
        
        return ZohoApi(tokens.access_token, store.location)
    except Exception as e:
        print(e)