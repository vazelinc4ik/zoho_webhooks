from abc import ABC
import os
from typing import Any, Dict

from ecwid_api import EcwidApi
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from zoho_api import ZohoApi

from crud import ItemsCRUD, OrdersCRUD

import logging

UNPAID_STATUS = 'AWAITING_PAYMENT'
PAID_STATUS = 'PAID'
REFUND_STATUS = 'REFUNDED'


def prepare_ecwid_data_for_zoho_contract(data: Dict[str, Any]) -> Dict[str, Any]:
    shipping_person = data.get('shippingPerson')
    billing_person = data.get('billingPerson')
    return {
        'contact_name': shipping_person.get('name'),
        'shipping_address': {
            'address': shipping_person.get('street'),
            'city': shipping_person.get('city'),
            'state': shipping_person.get('stateOrProvinceCode'),
            'zip': shipping_person.get('postalCode'),
            'country': shipping_person.get('countryCode')
        },
        'billing_address': {
            'address': billing_person.get('street'),
            'city': billing_person.get('city'),
            'state': billing_person.get('stateOrProvinceCode'),
            'zip': billing_person.get('postalCode'),
            'country': billing_person.get('countryCode')
        },
        'contact_persons': [{
            'first_name': shipping_person.get('firstName'),
            'last_name': shipping_person.get('lastName'),
            'email': data.get('email')
        }],
        
    }

async def handle_create_order_webhook(
    db: AsyncSession,
    event_data: Dict[str, str],
    ecwid_api: EcwidApi,
    zoho_api: ZohoApi
) -> None:
    try:
        
        payment_status = event_data.get('newPaymentStatus')
        order_id = event_data.get('orderId')
        
        if not order_id:
            return

        # Получаем данные заказа
        response_fields = 'email,items,shippingPerson,billingPerson'
        order_data = await ecwid_api.orders_client.get_order(order_id, responseFields=response_fields)
        
        customer_email = order_data.get('email')
        if not customer_email:
            return

        
        # Работа с контактом в Zoho
        try:
            customers = (await zoho_api.contacts_client.list_contacts(email=customer_email)).get('contacts', [])
            
            if customers:
                logging.info(customers)
                customer_id = customers[0]['contact_id']
            else:
                contact_payload = prepare_ecwid_data_for_zoho_contract(order_data)
                customer = await zoho_api.contacts_client.create_contact(**contact_payload)
                customer_id = customer['contact']['contact_id']
                
        except Exception as e:
            raise

        # Формируем заказ в Zoho
        zoho_payload = {
            'customer_id': customer_id,
            'line_items': [],
            'notes': 'Sales order from Ecwid'
        }

        
        items_processed = 0
        for item in order_data.get('items', []):
            product_id = item.get('productId')
            try:
                db_item = await ItemsCRUD.find_one_or_none(db, ecwid_item_id=product_id)
                if not db_item:
                    continue
                    
                zoho_payload['line_items'].append({
                    'item_id': db_item.zoho_item_id,
                    'rate': item.get('price'),
                    'quantity': item.get('quantity')
                })
                items_processed += 1
                
            except Exception as e:
                raise

        if not zoho_payload['line_items']:
            return

        
        # Создаем заказ в Zoho
        try:
            response = await zoho_api.sales_orders_client.create_sales_order(**zoho_payload)
            
            zoho_order_id = str(response.get("salesorder", {}).get('salesorder_id'))
            if not zoho_order_id:
                return
                
            
            # Сохраняем в базу данных
            try:
                await OrdersCRUD.create_entity(
                    db, 
                    store_id=1,
                    zoho_order_id=zoho_order_id,
                    ecwid_order_id=order_id
                )
            except Exception as e:
                raise
                
            # Подтверждаем оплаченный заказ
            if payment_status == PAID_STATUS:
                await zoho_api.sales_orders_client.confirm_sales_order(zoho_order_id)

                
        except Exception as e:
            raise
            
        
    except Exception as e:
        raise


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
    db: AsyncSession,
    event_data: Dict[str, str],
    zoho_api: ZohoApi
) -> None:
    order_id = event_data.get('orderId')
    order = await OrdersCRUD.find_one_or_none(db, ecwid_order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ecwid_id {order_id} not found")
    await zoho_api.sales_orders_client.delete_sales_order(order.zoho_order_id)

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
        await handle_delete_order_webhook(db, event_data, zoho_api)
    else:
        raise HTTPException(status_code=400, detail="Unknown event type")


