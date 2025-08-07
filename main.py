from ecwid_api import EcwidApi
from fastapi import (
    BackgroundTasks,
    Depends, 
    FastAPI,
    HTTPException,
    Path,
    Request
)
from sqlalchemy.ext.asyncio import AsyncSession


from utils.generators import get_ecwid_api, get_db, get_zoho_api
from utils.security import *
from utils.webhooks_hanlers import *

app = FastAPI()

def get_handler(
    webhook_type: str,
) -> type[WebhookHandlerProtocol]:
    match webhook_type:
        case "inventory-adjustment":
            return InventoryAdjustmentHandler
        case "sales":
            return SalesOrdersHandler
        case "purchase":
            return PurchaseOrdersHandfler
        case "transfer":
            return TransferOrdersHandler
        case _:
            raise HTTPException(
                status_code=400,
                detail="Unknown webhook type"
            )
        
def get_validator(
    webhook_type: str = Path(...),
) -> type[WebhookHandlerProtocol]:
    match webhook_type:
        case "inventory-adjustment":
            return ZohoInventoryWebhookValidator
        case "sales":
            return ZohoSalesWebhookValidator
        case "purchase":
            return ZohoPurchaseWebhookValidator
        case "transfer":
            return ZohoTransferWebhookValidator
        case _:
            raise HTTPException(
                status_code=400,
                detail="Unknown webhook type"
            )


@app.post("/zoho-webhooks/{webhook_type}")
async def adjust_eckwid_stock(
    request: Request,
    webhook_type: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    ecwid_api: EcwidApi = Depends(get_ecwid_api),
    handler: type[WebhookHandlerProtocol] = Depends(get_handler),
    validator: type[WebhookValidatorProtocol] = Depends(get_validator),
) -> dict:
    if not validator.validate(request):
        raise HTTPException(status_code=403, detail="Invalid signature")
    try:
        payload = await request.json()
        zoho_organization_id = request.headers.get("x-com-zoho-organizationid")
        background_tasks.add_task(handler.update_ecwid_stock_from_webhook, payload, zoho_organization_id, ecwid_api, db, webhook_type)
        return {"status": "received"}
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