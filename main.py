from fastapi import (
    Depends, 
    FastAPI,
    HTTPException, 
    Request
)


from utils.security import (
    ZohoSalesWebhookValidator,
    ZohoInventoryWebhookValidator
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
    request: Request
) -> dict:
    data = await request.json()
    print(data)
    return {"status": "ok"}
