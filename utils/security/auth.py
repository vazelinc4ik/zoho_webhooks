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