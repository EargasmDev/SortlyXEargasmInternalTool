from fastapi import APIRouter, Request
from datetime import datetime
import json
from app.database import get_db
from app.models import Job, JobItem

router = APIRouter()

@router.post("/sortly/webhook")
async def handle_sortly_webhook(request: Request):
    """
    Handles Sortly webhooks (transaction.created).
    Deducts quantity when an item moves out of 'Warehouse'.
    """
    raw = await request.body()
    try:
        data = json.loads(raw)
        print("\n🪵 RAW WEBHOOK PAYLOAD 🪵")
        print(json.dumps(data, indent=2))

        # Extract the main payload section (the "body")
        body = data.get("body", {})
        event_type = data.get("type", "unknown")

        # Extract relevant fields
        verb = body.get("verb", "").lower()
        item_name = body.get("node_name", "UNKNOWN")
        old_location = body.get("old_parent_name", "UNKNOWN")
        new_location = body.get("node_parent_name", "UNKNOWN")
        moved_qty = float(body.get("moved_quantity", 0))
        timestamp = data.get("time", datetime.utcnow().isoformat())

        print(f"📦 Webhook received: {event_type} | {item_name} ({verb}) {old_location} → {new_location} ({moved_qty})")

        # Only handle 'move' verbs that left Warehouse
        if verb == "move" and old_location == "Warehouse" and new_location != "Warehouse":
            db = next(get_db())
            job = db.query(Job).order_by(Job.id.desc()).first()
            if not job:
                print("⚠️ No active job found, skipping.")
                return {"status": "ignored", "reason": "no active job"}

            matched_item = None
            for i in job.items:
                # Fuzzy match: ignore case and allow substring match
                if item_name.lower() in i.name.lower() or i.name.lower() in item_name.lower():
                    matched_item = i
                    break

            if matched_item:
                deduct_amount = max(1, int(moved_qty))
                matched_item.current_qty = max(0, matched_item.current_qty - deduct_amount)
                db.commit()
                print(f"✅ Deducted {deduct_amount} from {matched_item.name}, new qty: {matched_item.current_qty}")
                return {
                    "status": "success",
                    "item": matched_item.name,
                    "deducted": deduct_amount,
                    "new_qty": matched_item.current_qty,
                    "timestamp": timestamp,
                }

            print(f"⚠️ No match found for item {item_name}")
            return {"status": "skipped", "reason": "no match", "item_name": item_name}

        print("ℹ️ Ignored non-move event or movement not from Warehouse.")
        return {"status": "ignored", "event": event_type, "verb": verb}

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"status": "error", "message": str(e)}
