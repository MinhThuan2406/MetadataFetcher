import os
import requests
from typing import Optional
from metadata_fetcher.config import GOOGLE_CSE_API_KEY, GOOGLE_CSE_ID, GOOGLE_CSE_URL


def google_search(query: str) -> Optional[str]:
    """
    Search Google Custom Search Engine for the query and return the top result URL.
    Returns None if no result or error.
    """
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
        print("[ERROR] Google CSE API key or CSE ID not set.")
        return None
    params = {
        'key': GOOGLE_CSE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': 1
    }
    try:
        response = requests.get(GOOGLE_CSE_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                return items[0].get('link')
        else:
            print(f"[ERROR] Google CSE API error: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Google CSE request failed: {e}")
    return None 