import os
import requests
from dotenv import load_dotenv

load_dotenv()

SORTLY_PUBLIC_KEY = os.getenv("SORTLY_PUBLIC_KEY")
SORTLY_SECRET_KEY = os.getenv("SORTLY_SECRET_KEY")
SORTLY_BASE_URL = os.getenv("SORTLY_BASE_URL", "https://api.sortly.co/api/v1")

if not SORTLY_SECRET_KEY:
    raise ValueError("Missing Sortly API credentials in .env")

HEADERS = {
    "Authorization": f"Bearer {SORTLY_SECRET_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_locations():
    """Fetch all locations from Sortly."""
    url = f"{SORTLY_BASE_URL}/locations"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Sortly API error: {res.status_code} - {res.text}")
    return res.json()

def get_items(location_id=None, name_query=None):
    """Fetch items (optionally filtered by location or name)."""
    url = f"{SORTLY_BASE_URL}/items"
    params = {}
    if location_id:
        params["filter[location_id]"] = location_id
    if name_query:
        params["filter[name]"] = name_query
    res = requests.get(url, headers=HEADERS, params=params)
    if res.status_code != 200:
        raise Exception(f"Sortly API error: {res.status_code} - {res.text}")
    return res.json()

def search_item_by_name(item_name):
    """Search Sortly by item name."""
    url = f"{SORTLY_BASE_URL}/items"
    params = {"filter[name]": item_name}
    res = requests.get(url, headers=HEADERS, params=params)
    if res.status_code != 200:
        raise Exception(f"Sortly API error: {res.status_code} - {res.text}")
    return res.json()

def deduct_item_quantity(item_id, new_quantity):
    """Update Sortly item quantity."""
    url = f"{SORTLY_BASE_URL}/items/{item_id}"
    data = {"quantity": new_quantity}
    res = requests.put(url, headers=HEADERS, json=data)
    if res.status_code not in (200, 204):
        raise Exception(f"Sortly API error: {res.status_code} - {res.text}")
    return True

def test_sortly_connection():
    """Quick connectivity test."""
    url = f"{SORTLY_BASE_URL}/items"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        print("✅ Sortly API connected successfully!")
        print(res.json())
    else:
        print(f"❌ Sortly API error: {res.status_code} - {res.text}")
