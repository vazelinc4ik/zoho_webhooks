
from typing import Any, Dict, List, Protocol

from fastapi import (
    HTTPException, 
    Request
)
from ecwid_api import EcwidApi
from sqlalchemy.ext.asyncio import AsyncSession

from core import settings
from crud import (
    ItemsCRUD,
    StoresCRUD,
    WebhookCRUD,
    WebhookItemCRUD
)
from models import (
    Items, 
    Stores
)

TARGET_WH_ID = settings.zoho_settings.zoho_warehouse_id
AMAZON_CUSTOMER_ID = settings.zoho_settings.amazon_customer_id

#TODO: Добавить отправку уведомлений в тг о несуществующем магазине или товаре

class WebhookHandlerProtocol(Protocol):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]: ...

    @staticmethod
    def _get_quantity_change_from_item(item: Dict[str, Any]) -> int: ...

    @classmethod
    async def update_ecwid_stock_from_webhook(
        cls,
        request: Request,
        ecwid_api: EcwidApi,
        db: AsyncSession,
        webhook_type: str
    ) -> Dict[str, dict]: ...

class BaseHandler:
    @staticmethod
    def _get_store_from_request(request: Request) -> Stores: 
        return request.headers.get("x-com-zoho-organizationid")
    
    @staticmethod
    async def _find_store_entity_in_database(
        db: AsyncSession,
        **data: Any
    ) -> Stores:
        store = await StoresCRUD.find_one_or_none(db, **data)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        return store
    
    @classmethod
    async def _find_item_entity_in_database(
        cls,
        store: Stores,
        db: AsyncSession,
        **kwargs: Any
    ) -> Items:
        data = {"store_id": store.id}
        data.update(kwargs)

        item = await ItemsCRUD.find_one_or_none(db, **data)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item
    
    @classmethod
    async def update_ecwid_stock_from_webhook(
        cls: type[WebhookHandlerProtocol],
        request: Request,
        ecwid_api: EcwidApi,
        db: AsyncSession,
        webhook_type: str
    ) -> Dict[str, dict]:
        zoho_organization_id = cls._get_store_from_request(request)

        store = await cls._find_store_entity_in_database(db, zoho_organization_id=zoho_organization_id)
        items_data = await cls._get_items_data_from_request(request)
        webhook = await WebhookCRUD.create_entity(
            db,
            type=webhook_type
        )
        for item in items_data:
            warehouse_id = item.get('warehouse_id', None)
            if warehouse_id and warehouse_id != TARGET_WH_ID:
                continue
            
            zoho_item_id = str(item.get('item_id'))

            db_item = await cls._find_item_entity_in_database(
                store=store,
                db=db,
                zoho_item_id=zoho_item_id
            )
            
            if not db_item:
                continue

            ecwid_item_id = db_item.ecwid_item_id
            quantity = cls._get_quantity_change_from_item(item)

            await ecwid_api.products_client.adjust_product_stock(ecwid_item_id, quantity)
            await WebhookItemCRUD.create_entity(
                db,
                webhook_id=webhook.id,
                item_id=db_item.id,
                quantity=quantity
            )

class InventoryAdjustmentHandler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('inventory_adjustment', {})

        if data.get('adjustment_type', "") != "quantity":
            raise HTTPException(status_code=400, detail="Unsupported adjustment type")

        return data.get('line_items', [])
    
    @staticmethod
    def _get_quantity_change_from_item(
        item: Dict[str, Any]
    ) -> int: return item.get('quantity_adjusted')

class SalesOrdersHandler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('salesorder', {})
        if data.get('customer_id', '') != AMAZON_CUSTOMER_ID:
            raise HTTPException(status_code=400, detail="Unsupported customer")
        return data.get('line_items', [])
    
    @staticmethod
    def _get_quantity_change_from_item(
        item: Dict[str, Any]
    ) -> int: return -item.get('quantity')


class PurchaseOrdersHandfler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('purchaseorder', {})
        return data.get('line_items', [])
    
    @staticmethod
    def _get_quantity_change_from_item(
        item: Dict[str, Any]
    ) -> int: return item.get('quantity')

class TransferOrdersHandler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('transfer_order', {})
        return data.get('line_items', [])

    @staticmethod
    def _get_quantity_change_from_item(
        item: Dict[str, Any]
    ) -> int: return -item.get('quantity_transfer')

