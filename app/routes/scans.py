from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models import Job, JobItem, Scan
from app.utils import fuzzy_match

router = APIRouter(prefix="/scan", tags=["scans"])


@router.post("")
def handle_scan(scan: dict):
    """
    Process a barcode scan:
    - Check job exists
    - Ensure barcode hasn’t been scanned in this job
    - Match scan to job item and decrement inventory
    """
    db = SessionLocal()
    try:
        job_name = scan.get("job_name")
        scanned_name = scan.get("scanned_name")
        location = scan.get("location", "")

        if not job_name or not scanned_name:
            raise HTTPException(status_code=400, detail="Missing job_name or scanned_name")

        job = db.query(Job).filter(Job.name == job_name).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check for duplicate barcode in same job
        existing_scan = (
            db.query(Scan)
            .filter(Scan.job_id == job.id, Scan.scanned_name == scanned_name)
            .first()
        )
        if existing_scan:
            raise HTTPException(status_code=400, detail="Barcode already scanned for this job")

        # Match scan to item
        matched_name = fuzzy_match(scanned_name, job.items)
        if not matched_name:
            raise HTTPException(status_code=404, detail="No matching item found for scan")

        item = next(i for i in job.items if i.name == matched_name)
        if item.current_qty <= 0:
            raise HTTPException(status_code=400, detail=f"Item '{item.name}' already depleted")

        # Deduct one unit
        item.current_qty -= 1

        # Log scan
        db_scan = Scan(job_id=job.id, scanned_name=scanned_name, location=location)
        db.add(db_scan)
        db.commit()

        return {"message": f"Scan recorded for '{matched_name}'. Remaining: {item.current_qty}"}
    finally:
        db.close()
