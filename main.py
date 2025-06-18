from typing import List, Literal, Optional, Union

from ecwid_api import EcwidApi
from fastapi import (
    Depends, 
    FastAPI,
    HTTPException,
    Query, 
    Request
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from zoho_api import ZohoApi

import requests

from utils.generators import get_ecwid_api, get_db, get_zoho_api
from crud import ZohoTokensCRUD
from utils.security import (
    ZohoSalesWebhookValidator,
    ZohoInventoryWebhookValidator,
    ZohoPurchaseWebhookValidator,
    generate_zoho_auth_uri,
    generate_zoho_tokens_url,
)
from utils.webhooks_hanlers import *

app = FastAPI()


@app.post("/zoho-webhooks/inventory-adjustment")
async def adjust_eckwid_inventory_by_user_input(
    request: Request,
    is_signature_valid: bool = Depends(ZohoInventoryWebhookValidator.validate_request),
    ecwid_api: EcwidApi = Depends(get_ecwid_api),
    db: AsyncSession = Depends(get_db)
) -> dict:
    if not is_signature_valid:
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        await InventoryAdjustmentHandler.update_ecwid_stock_from_webhook(request, ecwid_api, db)
        return {"status": "ok"}
    except HTTPException as exc:
        return {"status": "no action taken", "message": exc.detail}


@app.post("/zoho-webhooks/sales")
async def adjust_eckwid_inventory_by_fbm_sale(
    request: Request,
    is_signature_valid: bool = Depends(ZohoSalesWebhookValidator.validate_request),
    ecwid_api: EcwidApi = Depends(get_ecwid_api),
    db: AsyncSession = Depends(get_db)
) -> dict:
    if not is_signature_valid:
        raise HTTPException(status_code=403, detail="Invalid signature")
    try:
        await SalesOrdersHandler.update_ecwid_stock_from_webhook(request, ecwid_api, db)
        return {"status": "ok"}
    except HTTPException as exc:
        return {"status": "no action taken", "message": exc.detail}

@app.post("/zoho-webhooks/purchase")
async def adjust_eckwid_inventory_by_fbm_sale(
    request: Request,
    is_signature_valid: bool = Depends(ZohoPurchaseWebhookValidator.validate_request),
    ecwid_api: EcwidApi = Depends(get_ecwid_api),
    db: AsyncSession = Depends(get_db)
) -> dict:
    if not is_signature_valid:
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        await PurchaseOrdersHandfler.update_ecwid_stock_from_webhook(request, ecwid_api, db)
        return {"status": "ok"}
    except HTTPException as exc:
        return {"status": "no action taken", "message": exc.detail}

    
@app.post("/ecwid-webhooks/sales")
async def create_zoho_inventory_sales_order(
    request: Request,
    db: AsyncSession = Depends(get_db),
    ecwid_api: EcwidApi = Depends(get_ecwid_api),
) -> dict:
    data = await request.json()
    zoho_api = await get_zoho_api(data, db)
    event_type = data.get('eventType')
    event_data = data.get('data')
    try:
        await handle_ecwid_webhook(db, event_type, event_data, ecwid_api, zoho_api)
    except Exception as e:
        print(e)
    
    return {"status": "ok"}