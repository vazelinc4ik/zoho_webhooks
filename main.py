

import uvicorn
from fastapi import FastAPI, Request



app = FastAPI()

@app.post("/zoho-webhooks/inventory-adjustment")
async def adjust_eckwid_inventory(
    request: Request
) -> None:
    data = await request.json()
    print(data)

