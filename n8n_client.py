import aiohttp
import os
import logging

N8N_WEBHOOK_URL = "https://dektek.app.n8n.cloud/webhook/broker-rate-confirmation"

async def send_pdf_to_n8n(file_content: bytes, filename: str):
    """Sends PDF binary to n8n and returns the extracted JSON data."""
    data = aiohttp.FormData() 
    data.add_field('file', file_content, filename=filename, content_type='application/pdf')
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(N8N_WEBHOOK_URL, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"n8n error: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Request failed: {e}")
        return None