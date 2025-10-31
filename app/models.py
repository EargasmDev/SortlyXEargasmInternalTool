from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("JobItem", back_populates="job", cascade="all, delete-orphan")


class JobItem(Base):
    __tablename__ = "job_items"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    name = Column(String, nullable=False)
    current_qty = Column(Integer, default=0)
    job = relationship("Job", back_populates="items")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    scanned_name = Column(String)
    location = Column(String, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)


class SortlyItemState(Base):
    """
    Tracks the last known location and timestamp for Sortly items.
    Used to detect when an item leaves the Warehouse.
    """
    __tablename__ = "sortly_item_state"

    id = Column(Integer, primary_key=True, index=True)
    sortly_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    last_location = Column(String)
    last_seen = Column(DateTime)
