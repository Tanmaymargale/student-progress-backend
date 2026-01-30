from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import contest_ws

router = APIRouter()

# Read headers from Google Sheet
HEADERS = contest_ws.row_values(1)


# =========================
# Pydantic Models
# =========================

class ContestCreate(BaseModel):
    contest_id: int
    registration_id: int
    batch_id: int
    contest_name: str
    date: str
    score: Optional[float] = None
    rank: Optional[int] = None
    remark: Optional[str] = None


class ContestUpdate(BaseModel):
    registration_id: Optional[int] = None
    batch_id: Optional[int] = None
    contest_name: Optional[str] = None
    date: Optional[str] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    remark: Optional[str] = None


# =========================
# Helper Function
# =========================

def find_contest_row(contest_id: int):
    records = contest_ws.get_all_records()
    for index, row in enumerate(records, start=2):
        try:
            if int(row.get("contest_id")) == contest_id:
                return index, row
        except (ValueError, TypeError):
            continue
    return None, None


# =========================
# CREATE Contest
# =========================

@router.post("/")
def create_contest(contest: ContestCreate):

    row_number, _ = find_contest_row(contest.contest_id)
    if row_number:
        raise HTTPException(
            status_code=400,
            detail="Contest already exists"
        )

    contest_data = contest.model_dump()
    row = [contest_data.get(col, "") for col in HEADERS]
    contest_ws.append_row(row)

    return {"message": "Contest added successfully"}


# =========================
# READ All Contests
# =========================

@router.get("/")
def get_all_contests():
    return contest_ws.get_all_records()


# =========================
# READ One Contest
# =========================

@router.get("/{contest_id}")
def get_contest(contest_id: int):
    _, contest = find_contest_row(contest_id)
    if not contest:
        raise HTTPException(
            status_code=404,
            detail="Contest not found"
        )
    return contest


# =========================
# UPDATE Contest (Partial Update)
# =========================

@router.patch("/{contest_id}")
def update_contest(contest_id: int, updated_data: ContestUpdate):

    row_number, _ = find_contest_row(contest_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Contest not found"
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
            contest_ws.update_cell(row_number, col_index, value)

    return {"message": "Contest updated successfully"}


# =========================
# DELETE Contest
# =========================

@router.delete("/{contest_id}")
def delete_contest(contest_id: int):

    row_number, _ = find_contest_row(contest_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Contest not found"
        )

    contest_ws.delete_rows(row_number)
    return {"message": "Contest deleted successfully"}
