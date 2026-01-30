from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import batches_ws

router = APIRouter()

# Read headers from Google Sheet (row 1)
HEADERS = batches_ws.row_values(1)


# =========================
# Pydantic Models
# =========================

class BatchCreate(BaseModel):
    batch_id: int
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
# Helper Function
# =========================

def find_batch_row(batch_id: int):
    records = batches_ws.get_all_records()
    for index, row in enumerate(records, start=2):  # start=2 → after header
        if int(row.get("batch_id")) == batch_id:
            return index, row
    return None, None


# =========================
# CREATE Batch
# =========================

@router.post("/")
def create_batch(batch: BatchCreate):

    records = batches_ws.get_all_records()

    for r in records:
        if int(r.get("batch_id")) == batch.batch_id:
            raise HTTPException(
                status_code=400,
                detail="Batch already exists"
            )

    batch_data = batch.model_dump()

    # Align data with Google Sheet headers
    row = [batch_data.get(col, "") for col in HEADERS]
    batches_ws.append_row(row)

    return {"message": "Batch added successfully"}


# =========================
# READ All Batches
# =========================

@router.get("/")
def get_all_batches():
    return batches_ws.get_all_records()


# =========================
# READ One Batch
# =========================

@router.get("/{batch_id}")
def get_batch(batch_id: int):
    _, batch = find_batch_row(batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )
    return batch


# =========================
# UPDATE Batch (Partial Update)
# =========================

@router.patch("/{batch_id}")
def update_batch(
    batch_id: int,
    updated_data: BatchUpdate
):
    row_number, _ = find_batch_row(batch_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    update_dict = updated_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    for col, value in update_dict.items():
        if col in HEADERS:
            col_index = HEADERS.index(col) + 1
            batches_ws.update_cell(row_number, col_index, value)

    return {"message": "Batch updated successfully"}


# =========================
# DELETE Batch
# =========================

@router.delete("/{batch_id}")
def delete_batch(batch_id: int):
    row_number, _ = find_batch_row(batch_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    batches_ws.delete_rows(row_number)
    return {"message": "Batch deleted successfully"}
