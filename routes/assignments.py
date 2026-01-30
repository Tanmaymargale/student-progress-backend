from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import assignment_ws

router = APIRouter()

# Read headers from Google Sheet
HEADERS = assignment_ws.row_values(1)


# =========================
# Pydantic Models
# =========================

class AssignmentCreate(BaseModel):
    registration_id: int
    student_name: str
    assignment_title: str
    assignment_no: int
    assigned_date: str
    due_date: str
    submission_link: Optional[str] = None
    status: Optional[str] = "Pending"
    marks: Optional[float] = None


class AssignmentUpdate(BaseModel):
    student_name: Optional[str] = None
    assignment_title: Optional[str] = None
    assigned_date: Optional[str] = None
    due_date: Optional[str] = None
    submission_link: Optional[str] = None
    status: Optional[str] = None
    marks: Optional[float] = None


# =========================
# Helper Function
# =========================

def find_assignment_row(registration_id: int, assignment_no: int):
    records = assignment_ws.get_all_records()
    for index, row in enumerate(records, start=2):
        try:
            if int(row.get("registration_id")) == registration_id and int(row.get("assignment_no")) == assignment_no:
                return index, row
        except (ValueError, TypeError):
            continue
    return None, None


# =========================
# CREATE Assignment
# =========================

@router.post("/")
def create_assignment(assignment: AssignmentCreate):

    row_number, _ = find_assignment_row(assignment.registration_id, assignment.assignment_no)
    if row_number:
        raise HTTPException(
            status_code=400,
            detail="Assignment already exists for this student"
        )

    assignment_data = assignment.model_dump()
    row = [assignment_data.get(col, "") for col in HEADERS]
    assignment_ws.append_row(row)

    return {"message": "Assignment added successfully"}


# =========================
# READ All Assignments
# =========================

@router.get("/")
def get_all_assignments():
    return assignment_ws.get_all_records()


# =========================
# READ One Assignment
# =========================

@router.get("/{registration_id}/{assignment_no}")
def get_assignment(registration_id: int, assignment_no: int):
    _, assignment = find_assignment_row(registration_id, assignment_no)
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )
    return assignment


# =========================
# UPDATE Assignment (Partial Update)
# =========================

@router.patch("/{registration_id}/{assignment_no}")
def update_assignment(registration_id: int, assignment_no: int, updated_data: AssignmentUpdate):

    row_number, _ = find_assignment_row(registration_id, assignment_no)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
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
            assignment_ws.update_cell(row_number, col_index, value)

    return {"message": "Assignment updated successfully"}


# =========================
# DELETE Assignment
# =========================

@router.delete("/{registration_id}/{assignment_no}")
def delete_assignment(registration_id: int, assignment_no: int):

    row_number, _ = find_assignment_row(registration_id, assignment_no)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    assignment_ws.delete_rows(row_number)
    return {"message": "Assignment deleted successfully"}
