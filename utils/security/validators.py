import hmac
import hashlib

from typing import ClassVar

from fastapi import (
    Depends,
    HTTPException
)

from core.config import settings

from .helpers import (
    get_payload,
    get_zoho_signature
)

class BaseValidator:
    secret_key: ClassVar[str] = ""

    @classmethod
    def validate_request(
        cls,
        received_signature: str = Depends(get_zoho_signature),
        payload: bytes = Depends(get_payload),
    ) -> bool:
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
    