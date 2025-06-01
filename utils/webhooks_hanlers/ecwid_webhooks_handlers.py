from abc import ABC
from typing import Any, Dict

from ecwid_api import EcwidApi
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from zoho_api import ZohoApi

from crud import ItemsCRUD, OrdersCRUD

UNPAID_STATUS = 'AWAITING_PAYMENT'
PAID_STATUS = 'PAID'
REFUND_STATUS = 'REFUNDED'
CUSTOMER_ID = 696616000002368581


async def handle_create_order_webhook(
    db: AsyncSession,
    event_data: Dict[str, str],
    ecwid_api: EcwidApi,
    zoho_api: ZohoApi
) -> None:
    payment_status = event_data.get('newPaymentStatus')
    order_id = event_data.get('orderId')
    order_data = await ecwid_api.orders_client.get_order(order_id)
    zoho_payload = {
        'customer_id': CUSTOMER_ID,
        'line_items': []
    }

    for item in order_data.get('items', []):
        db_item = await ItemsCRUD.find_one_or_none(db, ecwid_item_id=item.get('productId'))
        zoho_payload['line_items'].append({
            'item_id': db_item.zoho_item_id,
            'rate': item.get('price'),
            'quantity': item.get('quantity')
        })

    response = await zoho_api.sales_orders_client.create_sales_order(**zoho_payload)
    print(response)
    zoho_order_id = str(response.get("salesorder", {}).get('salesorder_id'))
    await OrdersCRUD.create_entity(
        db, 
        store_id=1,
        zoho_order_id=zoho_order_id,
        ecwid_order_id=order_id
    )

    if payment_status == PAID_STATUS:
        await zoho_api.sales_orders_client.confirm_sales_order(zoho_order_id)

async def handle_update_order_webhook(
    db: AsyncSession,
    event_data: Dict[str, str],
    zoho_api: ZohoApi
) -> None:
    order_id = event_data.get("orderId")
    order = await OrdersCRUD.find_one_or_none(db, ecwid_order_id=order_id)
    old_payment_status = event_data.get("oldPaymentStatus")
    new_payment_status = event_data.get("newPaymentStatus")

    if old_payment_status == UNPAID_STATUS and new_payment_status == PAID_STATUS:
        await zoho_api.sales_orders_client.confirm_sales_order(order.zoho_order_id)
    elif old_payment_status != REFUND_STATUS and new_payment_status == REFUND_STATUS:
        await zoho_api.sales_orders_client.delete_sales_order(order.zoho_order_id)


async def handle_delete_order_webhook(
    event_data: Dict[str, str],
    zoho_api: ZohoApi
) -> None:
    order_id = event_data.get('orderId')
    await zoho_api.sales_orders_client.delete_sales_order(order_id)

async def handle_ecwid_webhook(
    db: AsyncSession,
    event_type: str,
    event_data: Dict[str, str],
    ecwid_api: EcwidApi,
    zoho_api: ZohoApi
) -> None:
    if event_type == 'order.created':
        await handle_create_order_webhook(db, event_data, ecwid_api, zoho_api)
    elif event_type == 'order.updated':
        await handle_update_order_webhook(db, event_data, zoho_api)
    elif event_type == 'order.deleted':
        await handle_delete_order_webhook(event_data, zoho_api)
    else:
        raise HTTPException(status_code=400, detail="Unknown event type")


