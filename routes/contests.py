from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import contest_ws

router = APIRouter()

# =========================
# Fixed headers
# =========================

HEADERS = [
    "contest_id",
    "registration_id",
    "batch_id",
    "contest_name",
    "date",
    "score",
    "rank",
    "remark",
]

# =========================
# Helpers
# =========================

def normalize_row(row):
    row = row + [""] * (len(HEADERS) - len(row))
    return dict(zip(HEADERS, row))


def find_contest_row(contest_id: int, registration_id: int):
    rows = contest_ws.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue

        try:
            if (
                row[0].strip() == str(contest_id)
                and row[1].strip() == str(registration_id)
            ):
                return i, normalize_row(row)
        except IndexError:
            continue

    return None, None


# =========================
# Models
# =========================

class ContestCreate(BaseModel):
    contest_id: int
    registration_id: int
    batch_id: int
    contest_name: str
    date: str
    score: Optional[float] = None
    rank: Optional[str] = None
    remark: Optional[str] = None


class ContestUpdate(BaseModel):
    batch_id: Optional[int] = None
    contest_name: Optional[str] = None
    date: Optional[str] = None
    score: Optional[float] = None
    rank: Optional[str] = None
    remark: Optional[str] = None


# =========================
# CREATE
# =========================

@router.post("/")
def create_contest(contest: ContestCreate):

    row_number, _ = find_contest_row(
        contest.contest_id,
        contest.registration_id,
    )

    if row_number:
        raise HTTPException(400, "Contest entry already exists")

    data = contest.model_dump()
    row = [data.get(col, "") for col in HEADERS]

    contest_ws.append_row(row)

    return {"message": "Contest added successfully"}


# =========================
# READ ALL
# =========================

@router.get("/")
def get_all_contests():

    rows = contest_ws.get_all_values()

    contests = []

    for row in rows[1:]:
        contests.append(normalize_row(row))

    return contests


# =========================
# READ ONE
# =========================

@router.get("/{contest_id}/{registration_id}")
def get_contest(contest_id: int, registration_id: int):

    _, contest = find_contest_row(contest_id, registration_id)

    if not contest:
        raise HTTPException(404, "Contest not found")

    return contest


# =========================
# UPDATE
# =========================

@router.patch("/{contest_id}/{registration_id}")
def update_contest(
    contest_id: int,
    registration_id: int,
    updated: ContestUpdate,
):

    row_number, _ = find_contest_row(contest_id, registration_id)

    if not row_number:
        raise HTTPException(404, "Contest not found")

    update_data = updated.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No fields to update")

    for col, value in update_data.items():
        if col in HEADERS:
            col_index = HEADERS.index(col) + 1
            contest_ws.update_cell(row_number, col_index, value)

    return {"message": "Contest updated successfully"}


# =========================
# DELETE
# =========================

@router.delete("/{contest_id}/{registration_id}")
def delete_contest(contest_id: int, registration_id: int):

    row_number, _ = find_contest_row(contest_id, registration_id)

    if not row_number:
        raise HTTPException(404, "Contest not found")

    contest_ws.delete_rows(row_number)

    return {"message": "Contest deleted successfully"}