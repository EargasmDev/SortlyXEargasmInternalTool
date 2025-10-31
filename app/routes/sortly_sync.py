from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import requests
from rapidfuzz import process
from app.database import get_db, Base, engine
from app.models import Job, JobItem
import os

router = APIRouter(prefix="/sortly", tags=["Sortly Sync"])

SORTLY_API_URL = "https://api.sortly.co/api/v1/items"
SORTLY_SECRET_KEY = os.getenv("SORTLY_SECRET_KEY")

# --- Internal cache table to track last sync time and location per item ---
from sqlalchemy import Column, Integer, String, DateTime

class SortlyCache(Base):
    __tablename__ = "sortly_cache"
    id = Column(Integer, primary_key=True, index=True)
    sortly_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    last_location = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)

# ✅ Correct way to create table
Base.metadata.create_all(bind=engine)


# --- Core utility function ---
def fuzzy_match(name, candidates):
    result = process.extractOne(name, candidates, score_cutoff=70)
    return result[0] if result else None


@router.get("/sync/{job_id}")
def sync_with_sortly(job_id: int, db: Session = Depends(get_db)):
    """
    Fetch updated Sortly items. 
    If an item moved out of 'Warehouse', deduct one in our local job.
    """

    headers = {"Authorization": f"Bearer {SORTLY_SECRET_KEY}"}

    # Find job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": f"Job {job_id} not found"}

    # Get last sync time
    last_seen = db.query(SortlyCache).order_by(SortlyCache.last_seen.desc()).first()
    updated_since = (
        (last_seen.last_seen - timedelta(minutes=10)).isoformat() + "Z"
        if last_seen else (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z"
    )

    url = f"{SORTLY_API_URL}?updated_since={updated_since}&per_page=100"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Sortly API error {response.status_code}: {response.text}")
        return {"error": response.text}

    data = response.json().get("data", [])
    matched = []
    skipped = []

    job_item_names = [i.name for i in job.items]

    for item in data:
        sortly_id = item.get("id")
        name = item.get("name")
        location = None

        # Extract location if available
        if "location" in item and isinstance(item["location"], dict):
            location = item["location"].get("name")
        elif "parent" in item and isinstance(item["parent"], dict):
            location = item["parent"].get("name")

        # Skip folders (Sortly marks them differently)
        if item.get("type") == "folder":
            skipped.append(name)
            continue

        # Get or create cache record
        cache = db.query(SortlyCache).filter(SortlyCache.sortly_id == sortly_id).first()
        if not cache:
            cache = SortlyCache(sortly_id=sortly_id, name=name, last_location=location)
            db.add(cache)
            db.commit()
            db.refresh(cache)

        # Detect movement out of Warehouse
        if cache.last_location == "Warehouse" and location and location != "Warehouse":
            matched_name = fuzzy_match(name, job_item_names)
            if matched_name:
                job_item = (
                    db.query(JobItem)
                    .filter(JobItem.job_id == job_id, JobItem.name == matched_name)
                    .first()
                )
                if job_item and job_item.current_qty > 0:
                    job_item.current_qty -= 1
                    db.commit()
                    matched.append({"name": matched_name, "new_qty": job_item.current_qty})

        # Update cache record regardless
        cache.last_location = location
        cache.last_seen = datetime.utcnow()
        db.commit()

    return {
        "job_id": job_id,
        "matched": matched,
        "skipped": skipped,
        "timestamp": datetime.utcnow().isoformat()
    }
