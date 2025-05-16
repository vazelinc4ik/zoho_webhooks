

import uvicorn
from fastapi import FastAPI, Request, Header



app = FastAPI()

@app.post("/zoho-webhooks/inventory-adjustment")
async def adjust_eckwid_inventory_by_user_input(
    request: Request,
) -> dict:
    data = await request.json()
    print("Headers:", dict(request.headers))
    print(data)
    return {"status": "ok"}

@app.post("/zoho-webhooks/sales")
async def adjust_eckwid_inventory_by_fbm_sale(
    request: Request
) -> dict:
    data = await request.json()
    print(data)
    return {"status": "ok"}

@app.post("/eckwid-webhooks/sales")
async def create_zoho_inventory_sales_order(
    request: Request
) -> dict:
    data = await request.json()
    print(data)
    return {"status": "ok"}
