

from abc import ABC, abstractmethod
from typing import Any

from fastapi import (
    Depends, 
    HTTPException, 
    Request
)

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
    async def _get_store_from_request(request: Request) -> Stores: 
        return request.headers.get("x-com-zoho-organizationid")
    
    @staticmethod
    @abstractmethod 
    def _get_items_data_from_request(request: Request): ...

    

    @classmethod
    @abstractmethod
    async def process_request(
        cls,
        request: Request
    ): ...
    
    @staticmethod
    async def _find_store_entity_in_database(**data: Any) -> Stores:
        store = await StoresCRUD.find_one_or_none(**data)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        return store

    @classmethod
    async def find_item_entity_in_database(
        cls,
        sku: str,
        store: Stores
    ) -> Items:
        data = {
            "store_id": store.id,
            "sku": sku
        }

        item = await ItemsCRUD.find_one_or_none(**data)
        if not store:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item

class ZohoWebhookHandler(BaseHandler):
    pass

