from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sheets import students_ws

router = APIRouter()

# Read header row from Google Sheet
HEADERS = students_ws.row_values(1)


# =========================
# Pydantic Models
# =========================

class StudentCreate(BaseModel):
    registration_id: int
    name: str
    email: EmailStr
    contact: str
    degree: str
    specialization: str
    batch_id: str
    fees: float
    fees_paid: float
    fees_pending: float
    placed: bool
    linkedin: Optional[str] = None
    github: Optional[str] = None
    resume: Optional[str] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    contact: Optional[str] = None
    degree: Optional[str] = None
    specialization: Optional[str] = None
    batch_id: Optional[str] = None
    fees: Optional[float] = None
    fees_paid: Optional[float] = None
    fees_pending: Optional[float] = None
    placed: Optional[bool] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    resume: Optional[str] = None


# =========================
# Helper Function (FIXED)
# =========================

def find_student_row(registration_id: int):
    all_rows = students_ws.get_all_values()  # RAW VALUES

    try:
        reg_col_index = HEADERS.index("registration_id")
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail="registration_id column not found in sheet"
        )

    for i in range(1, len(all_rows)):  # skip header
        row = all_rows[i]

        if len(row) <= reg_col_index:
            continue

        sheet_reg_id = row[reg_col_index].strip()

        if sheet_reg_id == str(registration_id):
            student = dict(zip(HEADERS, row))
            return i + 1, student  # Google Sheets row number

    return None, None


# =========================
# CREATE Student
# =========================

@router.post("/")
def create_student(student: StudentCreate):

    row_number, _ = find_student_row(student.registration_id)
    if row_number:
        raise HTTPException(
            status_code=400,
            detail="Student already exists"
        )

    student_data = student.model_dump()

    row = [student_data.get(col, "") for col in HEADERS]
    students_ws.append_row(row)

    return {"message": "Student added successfully"}


# =========================
# READ All Students
# =========================

@router.get("/")
def get_all_students():
    rows = students_ws.get_all_values()
    return [dict(zip(HEADERS, row)) for row in rows[1:]]


# =========================
# READ One Student (SEARCH)
# =========================

@router.get("/{registration_id}")
def get_student(registration_id: int):
    _, student = find_student_row(registration_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    return student


# =========================
# UPDATE Student
# =========================

@router.patch("/{registration_id}")
def update_student(
    registration_id: int,
    updated_data: StudentUpdate
):
    row_number, _ = find_student_row(registration_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
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
            students_ws.update_cell(row_number, col_index, value)

    return {"message": "Student updated successfully"}


# =========================
# DELETE Student
# =========================

@router.delete("/{registration_id}")
def delete_student(registration_id: int):
    row_number, _ = find_student_row(registration_id)
    if not row_number:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    students_ws.delete_rows(row_number)
    return {"message": "Student deleted successfully"}
