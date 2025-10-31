import os, json, datetime, requests
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("SORTLY_BASE_URL", "https://api.sortly.co/api/v1").rstrip("/")
KEY  = os.getenv("SORTLY_SECRET_KEY", "")

if not KEY:
    print("ERROR: SORTLY_SECRET_KEY is empty. Add it to .env (no quotes) and rerun.")
    raise SystemExit(1)

H = {"Authorization": f"Bearer {KEY}", "Accept": "application/json"}

def try_get(path, params=None, bytes_preview=400):
    url = f"{BASE}/{path.lstrip('/')}"
    try:
        r = requests.get(url, headers=H, params=params or {}, timeout=20)
        print(f"[{r.status_code}] GET {url}")
        print(r.text[:bytes_preview].replace("\n"," "))
        print()
        return r
    except Exception as e:
        print(f"[ERR] GET {url} -> {e}\n")
        return None

print("=== Sanity: items/locations ===")
try_get("items", {"per_page": 1})
try_get("locations", {"per_page": 5})

print("=== Activity/history candidates ===")
for path in [
  "update_history",
  "activities",
  "logs",
  "history",
  "transactions",
  "item_transactions",
  "items/transactions",
  "events",
]:
    print(f"--- Probing /{path} ---")
    try_get(path, {"per_page": 2})

print("=== Items updated_since (last 5 minutes) ===")
since = (datetime.datetime.utcnow() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
try_get("items", {"per_page": 5, "updated_since": since})
