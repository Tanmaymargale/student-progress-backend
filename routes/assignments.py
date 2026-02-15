from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from sheets import assignment_ws

router = APIRouter()

# =========================
# Fixed Headers (STRICT)
# =========================

HEADERS = [
    "registration_id",
    "student_name",
    "assignment_title",
    "assignment_no",
    "assigned_date",
    "due_date",
    "submission_link",
    "status",
    "marks",
]

# =========================
# Helpers
# =========================

def normalize_row(row):
    row = row + [""] * (len(HEADERS) - len(row))
    return dict(zip(HEADERS, row))


def find_assignment_row(registration_id: int, assignment_no: int):
    rows = assignment_ws.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue

        try:
            if (
                row[0].strip() == str(registration_id)
                and row[3].strip() == str(assignment_no)
            ):
                return i, normalize_row(row)
        except IndexError:
            continue

    return None, None


# =========================
# Models
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
# CREATE
# =========================

@router.post("/")
def create_assignment(assignment: AssignmentCreate):

    row_number, _ = find_assignment_row(
        assignment.registration_id,
        assignment.assignment_no,
    )

    if row_number:
        raise HTTPException(400, "Assignment already exists")

    data = assignment.model_dump()
    row = [data.get(col, "") for col in HEADERS]

    assignment_ws.append_row(row)

    return {"message": "Assignment added successfully"}


# =========================
# READ ALL
# =========================

@router.get("/")
def get_all_assignments():

    rows = assignment_ws.get_all_values()

    assignments = []

    for row in rows[1:]:
        assignments.append(normalize_row(row))

    return assignments


# =========================
# READ ONE
# =========================

@router.get("/{registration_id}/{assignment_no}")
def get_assignment(registration_id: int, assignment_no: int):

    _, assignment = find_assignment_row(
        registration_id,
        assignment_no,
    )

    if not assignment:
        raise HTTPException(404, "Assignment not found")

    return assignment


# =========================
# UPDATE
# =========================

@router.patch("/{registration_id}/{assignment_no}")
def update_assignment(
    registration_id: int,
    assignment_no: int,
    updated: AssignmentUpdate,
):

    row_number, _ = find_assignment_row(
        registration_id,
        assignment_no,
    )

    if not row_number:
        raise HTTPException(404, "Assignment not found")

    update_data = updated.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No fields to update")

    for col, value in update_data.items():
        if col in HEADERS:
            col_index = HEADERS.index(col) + 1
            assignment_ws.update_cell(row_number, col_index, value)

    return {"message": "Assignment updated successfully"}


# =========================
# DELETE
# =========================

@router.delete("/{registration_id}/{assignment_no}")
def delete_assignment(registration_id: int, assignment_no: int):

    row_number, _ = find_assignment_row(
        registration_id,
        assignment_no,
    )

    if not row_number:
        raise HTTPException(404, "Assignment not found")

    assignment_ws.delete_rows(row_number)

    return {"message": "Assignment deleted successfully"}