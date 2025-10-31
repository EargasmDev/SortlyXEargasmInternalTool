from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    items = Column(JSON, nullable=False)  # { "HF-Blue": 10, "HF-Trans": 8 }
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to scans
    scans = relationship(
        "Scan",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Job(id={self.id}, name='{self.name}')>"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Back reference to job
    job = relationship("Job", back_populates="scans")

    def __repr__(self):
        return f"<Scan(id={self.id}, job_id={self.job_id}, item='{self.item_name}', qty={self.quantity})>"
