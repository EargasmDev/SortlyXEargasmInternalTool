from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, JobItem, Scan

router = APIRouter(prefix="/scan", tags=["Scans"])

@router.post("/{job_id}")
def process_scan(job_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    Record a scan for an item within a job.
    Expected payload: {"barcode": "HF-Blue"}
    """
    barcode = payload.get("barcode")
    if not barcode:
        raise HTTPException(status_code=400, detail="Missing barcode")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    item = next((i for i in job.items if i.name == barcode), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item '{barcode}' not found in job")

    # ✅ Decrement item qty
    if item.current_qty > 0:
        item.current_qty -= 1
    else:
        raise HTTPException(status_code=400, detail=f"'{barcode}' already at zero")

    # ✅ Log scan record
    new_scan = Scan(job_id=job.id, item_name=barcode)
    db.add(new_scan)

    db.commit()
    db.refresh(item)

    return {
        "message": f"Scanned {barcode}, remaining: {item.current_qty}",
        "updated_qty": item.current_qty,
    }
