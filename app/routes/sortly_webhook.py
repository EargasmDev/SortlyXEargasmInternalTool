from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import os
import math

from app.database import get_db
from app.models import Job, JobItem, Scan

router = APIRouter(prefix="/sortly", tags=["Sortly Webhooks"])

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _warehouse_names() -> set[str]:
    # Optional: set multiple names via env, e.g. "Warehouse,Main Warehouse,WH"
    raw = os.getenv("WAREHOUSE_NAMES", "Warehouse")
    return {_norm(x) for x in raw.split(",") if x.strip()}

@router.post("/webhook")
async def sortly_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Sortly transaction webhooks.
    Deduct item qty when a move crosses the Warehouse boundary
    — both directions (out of warehouse and into warehouse).
    """
    payload = await request.json()
    try:
        evt_type = payload.get("type")
        body = payload.get("body", {}) or {}
        verb = _norm(body.get("verb"))
        node_type = _norm(body.get("node_type"))
        item_name = body.get("node_name") or ""
        moved_qty_raw = body.get("moved_quantity")

        try:
            moved_qty = int(math.floor(float(moved_qty_raw))) if moved_qty_raw is not None else 1
        except Exception:
            moved_qty = 1

        old_parent_name = body.get("old_parent_name") or ""
        new_parent_name = body.get("node_parent_name") or ""
        old_parent_n = _norm(old_parent_name)
        new_parent_n = _norm(new_parent_name)

        wh_names = _warehouse_names()

        print(
            f"🪵 RAW WEBHOOK: type={evt_type} verb={verb} node_type={node_type} "
            f"item='{item_name}' old='{old_parent_name}' -> new='{new_parent_name}' qty={moved_qty}"
        )

        # Only process item move events
        if evt_type != "sortly.company.transaction.created" or verb != "move" or node_type != "item":
            return {"status": "ignored"}

        # Crosses warehouse boundary?
        out_of_wh = old_parent_n in wh_names and new_parent_n not in wh_names
        into_wh  = new_parent_n in wh_names and old_parent_n not in wh_names

        if not (out_of_wh or into_wh):
            print("ℹ️ Not crossing warehouse boundary; no deduction.")
            return {"status": "ok", "note": "not crossing warehouse boundary"}

        # Find the most recent job that contains a matching item
        jobs = db.query(Job).order_by(Job.created_at.desc()).all()
        target_job = None
        target_item: JobItem | None = None

        for j in jobs:
            # Exact match first
            exact = next((i for i in j.items if _norm(i.name) == _norm(item_name)), None)
            if exact:
                target_job = j
                target_item = exact
                break
            # Fallback: loose contains either way
            loose = next(
                (i for i in j.items if _norm(item_name) in _norm(i.name) or _norm(i.name) in _norm(item_name)),
                None
            )
            if loose:
                target_job = j
                target_item = loose
                break

        if not target_job or not target_item:
            print(f"⚠️ No matching job item for '{item_name}'. Nothing deducted.")
            return {"status": "ok", "note": "no matching job item"}

        # Deduct for both directions (leaving or entering Warehouse)
        before_qty = target_item.current_qty or 0
        deduct_by = max(1, moved_qty)
        new_qty = max(0, before_qty - deduct_by)

        # Log a scan row for audit (optional but keeps history consistent)
        db.add(Scan(job_id=target_job.id, item_name=target_item.name))

        target_item.current_qty = new_qty
        db.commit()
        db.refresh(target_item)

        direction = "OUT_OF_WAREHOUSE" if out_of_wh else "INTO_WAREHOUSE"
        print(
            f"✅ DEDUCT ({direction}): '{target_item.name}' in job '{target_job.name}' "
            f"{before_qty} -> {new_qty} (−{deduct_by})"
        )

        return {
            "status": "ok",
            "job_id": target_job.id,
            "job_name": target_job.name,
            "item": target_item.name,
            "direction": direction,
            "qty_before": before_qty,
            "qty_after": new_qty,
            "deducted": deduct_by,
        }

    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        return {"status": "error", "detail": str(e)}
