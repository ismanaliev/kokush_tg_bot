"""
TMA (Telegram Mini App) utilities for authentication and data parsing
"""
import hmac
import hashlib
from typing import Dict, Optional
from urllib.parse import unquote_plus
import json
import logging

logger = logging.getLogger(__name__)


def verify_tma_init_data(init_data: str, bot_token: str) -> bool:
    """
    Verify Telegram Mini App init data
    
    Args:
        init_data: The initData from Telegram client
        bot_token: Your bot's token
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # Parse the init data
        data_check_string = "\n".join(
            f"{k}={v}"
            for k, v in sorted(
                {
                    k: v for k, v in [
                        item.split("=") for item in init_data.split("&")
                    ]
                    if k != "hash"
                }.items()
            )
        )
        
        # Get the hash
        init_data_dict = {
            k: v for k, v in [
                item.split("=") for item in init_data.split("&")
            ]
        }
        provided_hash = init_data_dict.get("hash")
        
        # Calculate expected hash
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = provided_hash == expected_hash
        logger.info(f"TMA validation result: {is_valid}")
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating TMA data: {e}")
        return False


def parse_tma_init_data(init_data: str) -> Optional[Dict]:
    """
    Parse Telegram Mini App initData
    
    Args:
        init_data: The initData from Telegram client
    
    Returns:
        Dictionary with parsed data or None if parsing fails
    """
    try:
        parsed = {}
        for item in init_data.split("&"):
            key, value = item.split("=")
            if key == "user":
                parsed[key] = json.loads(unquote_plus(value))
            elif key == "auth_date":
                parsed[key] = int(value)
            else:
                parsed[key] = unquote_plus(value)
        
        logger.debug(f"Parsed TMA data for user: {parsed.get('user', {}).get('id')}")
        return parsed
        
    except Exception as e:
        logger.error(f"Error parsing TMA data: {e}")
        return None


def get_user_from_tma(init_data: str) -> Optional[Dict]:
    """
    Extract user information from TMA init data
    
    Args:
        init_data: The initData from Telegram client
    
    Returns:
        User dictionary with id, first_name, last_name, username
    """
    parsed = parse_tma_init_data(init_data)
    if parsed and "user" in parsed:
        return parsed["user"]
    return None
