

import uvicorn
from fastapi import FastAPI, Request



app = FastAPI()

@app.post("/zoho-weebhooks/inventory-adjustment")
async def adjust_eckwid_inventory(
    request: Request
) -> None:
    print(request)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)