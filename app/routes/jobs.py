from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, JobItem, Scan  # 👈 include Scan
from app.schemas import JobInput

router = APIRouter(prefix="/job", tags=["Jobs"])

# ---------- CREATE ----------
@router.post("")
def create_job(job_input: JobInput, db: Session = Depends(get_db)):
    job = Job(name=job_input.name)
    for item in job_input.items:
        job.items.append(JobItem(name=item.name, current_qty=item.count))
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "name": job.name, "item_count": len(job.items)}

# ---------- LIST ----------
@router.get("/list/all")
def list_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return [
        {
            "id": j.id,
            "name": j.name,
            "items": [{"name": i.name, "current_qty": i.current_qty} for i in j.items],
        }
        for j in jobs
    ]

# ---------- UPDATE SINGLE ITEM ----------
@router.put("/{job_id}/item")
def update_single_item(job_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    Update quantity for a single item in a job.
    Expected payload: {"name": "HF-Blue", "count": 8}
    """
    name = payload.get("name")
    count = payload.get("count")

    if not name:
        raise HTTPException(status_code=400, detail="Missing item name")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    item = next((i for i in job.items if i.name == name), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item '{name}' not found in job")

    if count is None:
        raise HTTPException(status_code=400, detail="Missing count")

    item.current_qty = int(count)
    db.commit()
    db.refresh(item)

    return {"message": f"Item '{name}' updated to {count}."}

# ---------- BULK UPDATE ----------
@router.put("/{job_id}/update-items")
def update_job_items(job_id: int, payload: dict, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    items_data = payload.get("items", [])
    if not isinstance(items_data, list):
        raise HTTPException(status_code=400, detail="Invalid items payload")

    for item_data in items_data:
        name = item_data.get("name")
        qty = item_data.get("current_qty")

        if not name:
            continue

        existing_item = next((i for i in job.items if i.name == name), None)
        if existing_item:
            if isinstance(qty, int):
                existing_item.current_qty = qty
        else:
            job.items.append(JobItem(name=name, current_qty=qty or 0))

    db.commit()
    db.refresh(job)
    return {
        "message": f"Job {job.name} updated successfully",
        "items": [{"name": i.name, "current_qty": i.current_qty} for i in job.items],
    }

# ---------- DELETE ----------
@router.delete("/{job_name:path}")
def delete_job(job_name: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.name == job_name).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_name}' not found")
    db.delete(job)
    db.commit()
    return {"message": f"Deleted job '{job_name}'"}

# ---------- READ SCANS FOR A JOB (NO TIMESTAMP REQUIRED) ----------
@router.get("/{job_id}/scans")
def get_scanned_items(
    job_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Return most recent scans for a job. We sort by Scan.id DESC (no timestamp needed).
    Response shape is minimal and matches existing schema.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    scans = (
        db.query(Scan)
        .filter(Scan.job_id == job_id)
        .order_by(Scan.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": s.id,
            "item_name": getattr(s, "item_name", None),  # keep it defensive
        }
        for s in scans
    ]
