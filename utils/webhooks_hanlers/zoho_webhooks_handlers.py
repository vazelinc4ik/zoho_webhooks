

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from fastapi import (
    Depends, 
    HTTPException, 
    Request
)
from ecwid_api import EcwidApi

from crud import (
    ItemsCRUD,
    StoresCRUD
)

from models import (
    Items, 
    Stores
)

#TODO: Добавить отправку уведомлений в тг о несуществующем магазине или товаре



class BaseHandler(ABC):

    @staticmethod
    @abstractmethod 
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]: ...

    @staticmethod
    def _get_quantity_change_from_item(
        item: Dict[str, Any]
    ) -> int: return item.get('quantity')

    @staticmethod
    def _get_store_from_request(request: Request) -> Stores: 
        return request.headers.get("x-com-zoho-organizationid")
    
    @staticmethod
    async def _find_store_entity_in_database(**data: Any) -> Stores:
        store = await StoresCRUD.find_one_or_none(**data)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        return store
    
    @classmethod
    async def _find_item_entity_in_database(
        cls,
        store: Stores,
        **kwargs: Any
    ) -> Items:
        data = {"store_id": store.id}
        data.update(kwargs)

        item = await ItemsCRUD.find_one_or_none(**data)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item
    
    @classmethod
    async def update_ecwid_stock_from_webhook(
        cls,
        request: Request,
        ecwid_api: EcwidApi
    ) -> Dict[str, dict]:
        zoho_organization_id = cls._get_store_from_request(request)
        try: 
            store = await cls._find_store_entity_in_database(zoho_organization_id=zoho_organization_id)
        except Exception as e:
            print(f"Store exc: {e}")

        try:
            items_data = await cls._get_items_data_from_request(request)
        except Exception as e:
            print(f"Items data exc: {e}")
        
        for item in items_data:
            zoho_item_id = str(item.get('item_id'))
            print(zoho_item_id)

            db_item = await cls._find_item_entity_in_database(
                store=store,
                zoho_item_id=zoho_item_id
            )
            print(db_item.id)
            ecwid_item_id = db_item.ecwid_item_id
            quantity = cls._get_quantity_change_from_item(item)
            ecwid_api.products_client.adjust_product_stock(ecwid_item_id, quantity)



class InventoryAdjustmentHandler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('inventory_adjustment', {})
        if data.get('adjustment_type', "") != "quantity":
            raise HTTPException(status_code=400, detail="Unsupported adjustment_type")
        return data.get('line_items', [])

    
class SalesOrdersHandler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('salesorder', {})
        if data.get('source', "") != "FBM_marker":
            raise HTTPException(status_code=400, detail="Unsupported source")  
        print(data)
        return []
        # return data.get('line_items', [])


class PurchaseOrdersHandfler(BaseHandler):
    @staticmethod
    async def _get_items_data_from_request(request: Request) -> List[Dict[str, Any]]:
        payload = await request.json()
        data = payload.get('purchaseorder', {})
        return data.get('line_items', [])



