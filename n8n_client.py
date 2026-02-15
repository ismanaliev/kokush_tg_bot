import aiohttp
import os
import logging

N8N_WEBHOOK_URL = "https://erta.app.n8n.cloud/webhook-test/435ccc03-0726-42aa-ac88-f664823b29b6"

async def push_to_n8n(load_obj, driver_obj=None, action="load_created"):
    payload = {
        "action": action,
        "load": {
            "id": load_obj.external_load_id,
            "pickup": load_obj.pickup_time.isoformat(),
            "status": load_obj.status
        },
        "driver": {
            "name": driver_obj.name if driver_obj else "Unassigned",
            "tg_id": driver_obj.telegram_id if driver_obj else None
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(N8N_WEBHOOK_URL, json=payload) as resp:
                return resp.status == 200
        except Exception as e:
            logging.error(f"n8n Connection Failed: {e}")
            return False