from fastapi import APIRouter, Request
from datetime import datetime
import os
import json
import math

from app.database import get_db
from app.models import Job

router = APIRouter()

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _warehouse_names() -> set[str]:
    # Optional: WAREHOUSE_NAMES="Warehouse,Main Warehouse,WH"
    raw = os.getenv("WAREHOUSE_NAMES", "Warehouse")
    return {_norm(x) for x in raw.split(",") if x.strip()}

@router.post("/sortly/webhook")
async def handle_sortly_webhook(request: Request):
    """
    Handle Sortly transaction webhooks (transaction.created).
    Deduct quantity when an item move crosses the Warehouse boundary
    (both directions: OUT of warehouse and INTO warehouse).
    """
    raw = await request.body()
    try:
        data = json.loads(raw)
        print("\n🪵 RAW WEBHOOK PAYLOAD 🪵")
        print(json.dumps(data, indent=2))

        body = data.get("body", {}) or {}
        event_type = data.get("type", "unknown")

        verb = (body.get("verb") or "").lower()
        node_type = (body.get("node_type") or "").lower()
        item_name = body.get("node_name") or "UNKNOWN"

        old_location = body.get("old_parent_name") or "UNKNOWN"
        new_location = body.get("node_parent_name") or "UNKNOWN"

        moved_qty_raw = body.get("moved_quantity")
        try:
            moved_qty = int(math.floor(float(moved_qty_raw))) if moved_qty_raw is not None else 1
        except Exception:
            moved_qty = 1
        deduct_amount = max(1, moved_qty)

        timestamp = data.get("time", datetime.utcnow().isoformat())

        print(f"📦 Webhook received: {event_type} | {item_name} ({verb}) {old_location} → {new_location} ({deduct_amount})")

        # Only item moves
        if event_type != "sortly.company.transaction.created" or verb != "move" or node_type != "item":
            print("ℹ️ Ignored: not an item move event.")
            return {"status": "ignored", "event": event_type, "verb": verb, "node_type": node_type}

        wh = _warehouse_names()
        old_is_wh = _norm(old_location) in wh
        new_is_wh = _norm(new_location) in wh

        # Only act when crossing the warehouse boundary (either direction)
        if not (old_is_wh ^ new_is_wh):
            print("ℹ️ Not crossing warehouse boundary; no deduction.")
            return {"status": "ignored", "note": "no warehouse boundary crossing"}

        # Get most recent job
        db = next(get_db())
        job = db.query(Job).order_by(Job.id.desc()).first()
        if not job:
            print("⚠️ No active job found, skipping.")
            return {"status": "ignored", "reason": "no active job"}

        # Fuzzy match item within that job
        target_item = None
        item_name_n = _norm(item_name)
        for i in job.items:
            inorm = _norm(i.name)
            if item_name_n == inorm or item_name_n in inorm or inorm in item_name_n:
                target_item = i
                break

        if not target_item:
            print(f"⚠️ No match found for item '{item_name}' in job '{job.name}'")
            return {"status": "skipped", "reason": "no match", "item_name": item_name, "job": job.name}

        # Deduct for both directions
        before = target_item.current_qty or 0
        after = max(0, before - deduct_amount)
        target_item.current_qty = after
        db.commit()

        direction = "OUT_OF_WAREHOUSE" if (old_is_wh and not new_is_wh) else "INTO_WAREHOUSE"
        print(f"✅ Deducted {deduct_amount} ({direction}) from '{target_item.name}' in job '{job.name}': {before} → {after}")

        return {
            "status": "success",
            "direction": direction,
            "job_id": job.id,
            "job_name": job.name,
            "item": target_item.name,
            "deducted": deduct_amount,
            "qty_before": before,
            "qty_after": after,
            "timestamp": timestamp,
        }

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"status": "error", "message": str(e)}
