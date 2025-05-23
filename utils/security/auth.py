from typing import List, Optional
from urllib.parse import urlencode

from core import settings

def generate_zoho_auth_uri(
    scopes: Optional[List[str]]
) -> str:
    base_url = "https://accounts.zoho.com/oauth/v2/auth"
    params = {
        'client_id': settings.zoho_settings.client_id,
        'scope': ', '.join(scopes) if scopes else "ZohoInventory.FullAccess.all",
        'response_type': 'code',
        'redirect_uri': settings.zoho_settings.zoho_callback_uri,
        'access_type': 'offline'
    }
    
    return f"{base_url}?{urlencode(params)}"

def generate_zoho_tokens_url(
    code: str,
) -> str:
    base_url = "https://accounts.zoho.eu/oauth/v2/token"
    params = {
        'code': code,
        'client_id': settings.zoho_settings.client_id,
        'client_secret': settings.zoho_settings.client_secret,
        'redirect_uri': settings.zoho_settings.zoho_callback_uri,
        'grant_type': 'authorization_code'
    }

    return f"{base_url}?{urlencode(params)}"

def generate_zoho_refresh_url(
    refresh_token: str,
) -> str:
    base_url = "https://accounts.zoho.eu/oauth/v2/token"
    params = {
        'refresh_token': refresh_token,
        'client_id': settings.zoho_settings.client_id,
        'client_secret': settings.zoho_settings.client_secret,
        'redirect_uri': settings.zoho_settings.zoho_callback_uri,
        'grant_type': 'refresh_token'
    }

    return f"{base_url}?{urlencode(params)}"