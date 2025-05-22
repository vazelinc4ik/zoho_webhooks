from typing import List, Optional
from fastapi import (
    Depends, 
    FastAPI,
    HTTPException,
    Query, 
    Request
)
from fastapi.responses import RedirectResponse
import requests

from utils.security import (
    ZohoSalesWebhookValidator,
    ZohoInventoryWebhookValidator,
    generate_zoho_auth_uri,
    generate_zoho_tokens_url,
)

app = FastAPI()

@app.post("/zoho-webhooks/inventory-adjustment")
async def adjust_eckwid_inventory_by_user_input(
    request: Request,
    is_signature_valid: bool = Depends(ZohoInventoryWebhookValidator.validate_request)
) -> dict:
    
    if not is_signature_valid:
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    payload = await request.json()

    print(payload)

    return {"status": "ok"}

@app.post("/zoho-webhooks/sales")
async def adjust_eckwid_inventory_by_fbm_sale(
    request: Request,
    is_signature_valid: bool = Depends(ZohoSalesWebhookValidator.validate_request)
) -> dict:
    if not is_signature_valid:
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    payload = await request.json()

    print(payload)

    return {"status": "ok"}

@app.post("/eckwid-webhooks/sales")
async def create_zoho_inventory_sales_order(
    request: Request
) -> dict:
    data = await request.json()
    print(data)
    return {"status": "ok"}

@app.get("/auth/zoho/callback")
async def proceed_zoho_callback(
    code: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
) -> dict:
    if error:
        return {"error": f"Zoho OAuth error: {error}"}
    
    tokens_url = generate_zoho_tokens_url(code)
    print(tokens_url)
    response = requests.post(url=tokens_url)

    print("Zoho response:", response.text)

    return {"status": "ok"}

@app.get("/auth/zoho")
async def auth_app_in_zoho(
    scopes: Optional[List[str]] = Query(None)
) -> RedirectResponse:
    redirect_url = generate_zoho_auth_uri(scopes)
    return RedirectResponse(url=redirect_url)
