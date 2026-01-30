from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import mock_ws

router = APIRouter()

# Read headers from Google Sheet
HEADERS = mock_ws.row_values(1)


# =========================
# Pydantic Models
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
    registration_id: Optional[int] = None
    batch_id: Optional[int] = None
    interviewer: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: Optional[str] = None


# =========================
# Helper Function
# =========================

def find_mock_row(mock_id: int):
    records = mock_ws.get_all_records()
    for index, row in enumerate(records, start=2):
        try:
            if int(row.get("mock_id")) == mock_id:
                return index, row
        except (ValueError, TypeError):
            continue
    return None, None


# =========================
# CREATE Mock
# =========================

@router.post("/")
def create_mock(mock: MockCreate):

    row_number, _ = find_mock_row(mock.mock_id)
    if row_number:
        raise HTTPException(
            status_code=400,
            detail="Mock interview already exists"
        )

    mock_data = mock.model_dump()
    row = [mock_data.get(col, "") for col in HEADERS]
    mock_ws.append_row(row)

    return {"message": "Mock interview added successfully"}


# =========================
# READ All Mocks
# =========================

@router.get("/")
def get_all_mocks():
    return mock_ws.get_all_records()


# =========================
# READ One Mock
# =========================

@router.get("/{mock_id}")
def get_mock(mock_id: int):
    _, mock = find_mock_row(mock_id)
    if not mock:
        raise HTTPException(
            status_code=404,
            detail="Mock interview not found"
        )
    return mock


# =========================
# UPDATE Mock (Partial Update)
# =========================

@router.patch("/{mock_id}")
def update_mock(mock_id: int, updated_data: MockUpdate):

    row_number, _ = find_mock_row(mock_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Mock interview not found"
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
            mock_ws.update_cell(row_number, col_index, value)

    return {"message": "Mock interview updated successfully"}


# =========================
# DELETE Mock
# =========================

@router.delete("/{mock_id}")
def delete_mock(mock_id: int):

    row_number, _ = find_mock_row(mock_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Mock interview not found"
        )

    mock_ws.delete_rows(row_number)
    return {"message": "Mock interview deleted successfully"}
