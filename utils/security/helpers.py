from fastapi import Request


async def get_payload(request: Request) -> bytes:
    return await request.body() 

async def get_zoho_signature(request: Request) -> str:
    return request.headers.get('x-zoho-webhook-signature')