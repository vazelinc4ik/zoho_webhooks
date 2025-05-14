

import uvicorn
from fastapi import FastAPI, Request



app = FastAPI()

@app.post("/zoho-weebhooks/inventory-adjustment")
async def adjust_eckwid_inventory(
    request: Request
) -> None:
    print(request)

