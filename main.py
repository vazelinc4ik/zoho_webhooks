

import uvicorn
from fastapi import FastAPI, Request



app = FastAPI()

@app.post("/zoho-webhooks/inventory-adjustment")
async def adjust_eckwid_inventory(
    request: Request
) -> dict:
    data = await request.json()
    print(data)
    return {"status": "ok"}

@app.post("/zoho-webhooks/sales")
async def adjust_eckwid_inventory(
    request: Request
) -> dict:
    data = await request.json()
    print(data)
    return {"status": "ok"}
