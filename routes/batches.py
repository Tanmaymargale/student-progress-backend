from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import batches_ws

router = APIRouter()

# =========================
# Fixed headers
# =========================

HEADERS = [
    "batch_id",
    "start_date",
    "end_date",
    "meeting_link",
    "fees",
    "total_students",
]

# =========================
# Helpers
# =========================

def normalize_row(row):
    row = row + [""] * (len(HEADERS) - len(row))
    return dict(zip(HEADERS, row))


def find_batch_row(batch_id: str):
    rows = batches_ws.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue

        if row[0].strip() == str(batch_id):
            return i, normalize_row(row)

    return None, None


# =========================
# Models
# =========================

class BatchCreate(BaseModel):
    batch_id: str   # 🔥 allow B999 style IDs
    start_date: str
    end_date: str
    meeting_link: Optional[str] = None
    fees: float
    total_students: int


class BatchUpdate(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    meeting_link: Optional[str] = None
    fees: Optional[float] = None
    total_students: Optional[int] = None


# =========================
# CREATE
# =========================

@router.post("/")
def create_batch(batch: BatchCreate):
    row_number, _ = find_batch_row(batch.batch_id)

    if row_number:
        raise HTTPException(400, "Batch already exists")

    data = batch.model_dump()
    row = [data.get(col, "") for col in HEADERS]

    batches_ws.append_row(row)

    return {"message": "Batch added successfully"}


# =========================
# READ ALL
# =========================

@router.get("/")
def get_all_batches():
    rows = batches_ws.get_all_values()

    batches = []

    for row in rows[1:]:
        batches.append(normalize_row(row))

    return batches


# =========================
# READ ONE
# =========================

@router.get("/{batch_id}")
def get_batch(batch_id: str):
    _, batch = find_batch_row(batch_id)

    if not batch:
        raise HTTPException(404, "Batch not found")

    return batch


# =========================
# UPDATE
# =========================

@router.patch("/{batch_id}")
def update_batch(batch_id: str, updated: BatchUpdate):
    row_number, _ = find_batch_row(batch_id)

    if not row_number:
        raise HTTPException(404, "Batch not found")

    update_data = updated.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No fields to update")

    for col, value in update_data.items():
        if col in HEADERS:
            col_index = HEADERS.index(col) + 1
            batches_ws.update_cell(row_number, col_index, value)

    return {"message": "Batch updated successfully"}


# =========================
# DELETE
# =========================

@router.delete("/{batch_id}")
def delete_batch(batch_id: str):
    row_number, _ = find_batch_row(batch_id)

    if not row_number:
        raise HTTPException(404, "Batch not found")

    batches_ws.delete_rows(row_number)

    return {"message": "Batch deleted successfully"}