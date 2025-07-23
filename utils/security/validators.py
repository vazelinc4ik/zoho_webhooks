import hmac
import hashlib

from typing import ClassVar, Protocol

from fastapi import (
    HTTPException,
    Request
)
from core.config import settings

class WebhookValidatorProtocol(Protocol):
    secret_key: ClassVar[str]

    @classmethod
    async def validate(
        cls,
        request: Request
    ) -> bool: ...

class BaseValidator:
    secret_key: ClassVar[str] = ""

    @staticmethod
    async def _get_payload(request: Request) -> bytes:
        return await request.body() 

    @staticmethod
    async def _get_zoho_signature(request: Request) -> str:
        return request.headers.get('x-zoho-webhook-signature')

    @classmethod
    async def validate(
        cls,
        request: Request
    ) -> bool:
        received_signature = await cls._get_zoho_signature(request)
        payload = await cls._get_payload(request)
        if not cls.secret_key:
            raise NotImplementedError(f"{cls.__name__}: secret_key must be set in child class!")
        
        if not received_signature:
            raise HTTPException(status_code=400, detail="Missing signature header")

        computed_signature = hmac.new(
            cls.secret_key.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_signature, received_signature)
    
    
class ZohoInventoryWebhookValidator(BaseValidator):
    secret_key = settings.zoho_settings.zoho_inventory_adjustment_secret

class ZohoSalesWebhookValidator(BaseValidator):
    secret_key = settings.zoho_settings.zoho_fbm_sales_secret

class ZohoPurchaseWebhookValidator(BaseValidator):
    secret_key = settings.zoho_settings.zoho_purchase_secret

class ZohoTransferWebhookValidator(BaseValidator):
    secret_key = settings.zoho_settings.zoho_transfer_secret 
    