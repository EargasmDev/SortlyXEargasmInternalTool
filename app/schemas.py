from pydantic import BaseModel
from typing import List


class ItemInput(BaseModel):
    name: str
    count: int


class JobInput(BaseModel):
    name: str
    items: List[ItemInput]


class ScanInput(BaseModel):
    job_name: str
    scanned_name: str
    location: str


class JobItemOut(BaseModel):
    name: str
    current_qty: int


class JobOut(BaseModel):
    job: str
    active_items: List[JobItemOut]
