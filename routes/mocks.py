from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import mock_ws

router = APIRouter()

# =========================
# Fixed headers
# =========================

HEADERS = [
    "mock_id",
    "registration_id",
    "batch_id",
    "interviewer",
    "score",
    "feedback",
    "status",
]

# =========================
# Helpers
# =========================

def normalize_row(row):
    row = row + [""] * (len(HEADERS) - len(row))
    return dict(zip(HEADERS, row))


def find_mock_row(mock_id: int, registration_id: int):
    rows = mock_ws.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue

        try:
            if (
                row[0].strip() == str(mock_id)
                and row[1].strip() == str(registration_id)
            ):
                return i, normalize_row(row)
        except IndexError:
            continue

    return None, None


# =========================
# Models
# =========================

class MockCreate(BaseModel):
    mock_id: int
    registration_id: int
    batch_id: int
    interviewer: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: Optional[str] = "Pending"


class MockUpdate(BaseModel):
    batch_id: Optional[int] = None
    interviewer: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: Optional[str] = None


# =========================
# CREATE
# =========================

@router.post("/")
def create_mock(mock: MockCreate):

    row_number, _ = find_mock_row(
        mock.mock_id,
        mock.registration_id,
    )

    if row_number:
        raise HTTPException(400, "Mock interview already exists")

    data = mock.model_dump()
    row = [data.get(col, "") for col in HEADERS]

    mock_ws.append_row(row)

    return {"message": "Mock interview added successfully"}


# =========================
# READ ALL
# =========================

@router.get("/")
def get_all_mocks():

    rows = mock_ws.get_all_values()

    mocks = []

    for row in rows[1:]:
        mocks.append(normalize_row(row))

    return mocks


# =========================
# READ ONE
# =========================

@router.get("/{mock_id}/{registration_id}")
def get_mock(mock_id: int, registration_id: int):

    _, mock = find_mock_row(mock_id, registration_id)

    if not mock:
        raise HTTPException(404, "Mock interview not found")

    return mock


# =========================
# UPDATE
# =========================

@router.patch("/{mock_id}/{registration_id}")
def update_mock(
    mock_id: int,
    registration_id: int,
    updated: MockUpdate,
):

    row_number, _ = find_mock_row(mock_id, registration_id)

    if not row_number:
        raise HTTPException(404, "Mock interview not found")

    update_data = updated.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No fields to update")

    for col, value in update_data.items():
        if col in HEADERS:
            col_index = HEADERS.index(col) + 1
            mock_ws.update_cell(row_number, col_index, value)

    return {"message": "Mock interview updated successfully"}


# =========================
# DELETE
# =========================

@router.delete("/{mock_id}/{registration_id}")
def delete_mock(mock_id: int, registration_id: int):

    row_number, _ = find_mock_row(mock_id, registration_id)

    if not row_number:
        raise HTTPException(404, "Mock interview not found")

    mock_ws.delete_rows(row_number)

    return {"message": "Mock interview deleted successfully"}