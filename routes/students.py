from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sheets import students_ws

router = APIRouter()

# =========================
# Headers (fixed structure)
# =========================

HEADERS = [
    "registration_id",
    "name",
    "email",
    "contact",
    "degree",
    "specialization",
    "batch_id",
    "fees",
    "fees_paid",
    "fees_pending",
    "placed",
    "linkedin",
    "github",
    "resume",
]

# =========================
# Helpers
# =========================

def to_bool(value):
    if isinstance(value, bool):
        return value

    if not value:
        return False

    value = str(value).strip().lower()
    return value in ["true", "yes", "1"]


def normalize_row(row):
    """Ensure row matches headers length"""
    row = row + [""] * (len(HEADERS) - len(row))
    return dict(zip(HEADERS, row))


def find_student_row(registration_id: int):
    rows = students_ws.get_all_values()

    for i, row in enumerate(rows[1:], start=2):
        if not row:
            continue

        if row[0].strip() == str(registration_id):
            student = normalize_row(row)
            student["placed"] = to_bool(student.get("placed"))
            return i, student

    return None, None


# =========================
# Models
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
# CREATE
# =========================

@router.post("/")
def create_student(student: StudentCreate):
    row_number, _ = find_student_row(student.registration_id)

    if row_number:
        raise HTTPException(400, "Student already exists")

    data = student.model_dump()
    data["placed"] = str(data["placed"]).upper()

    row = [data.get(col, "") for col in HEADERS]
    students_ws.append_row(row)

    return {"message": "Student added successfully"}


# =========================
# READ ALL
# =========================

@router.get("/")
def get_all_students():
    rows = students_ws.get_all_values()

    students = []

    for row in rows[1:]:
        student = normalize_row(row)
        student["placed"] = to_bool(student.get("placed"))
        students.append(student)

    return students


# =========================
# READ ONE
# =========================

@router.get("/{registration_id}")
def get_student(registration_id: int):
    _, student = find_student_row(registration_id)

    if not student:
        raise HTTPException(404, "Student not found")

    return student


# =========================
# UPDATE
# =========================

@router.patch("/{registration_id}")
def update_student(registration_id: int, updated: StudentUpdate):
    row_number, _ = find_student_row(registration_id)

    if not row_number:
        raise HTTPException(404, "Student not found")

    update_data = updated.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No fields to update")

    if "placed" in update_data:
        update_data["placed"] = str(update_data["placed"]).upper()

    for col, value in update_data.items():
        if col in HEADERS:
            col_index = HEADERS.index(col) + 1
            students_ws.update_cell(row_number, col_index, value)

    return {"message": "Student updated successfully"}


# =========================
# DELETE
# =========================

@router.delete("/{registration_id}")
def delete_student(registration_id: int):
    row_number, _ = find_student_row(registration_id)

    if not row_number:
        raise HTTPException(404, "Student not found")

    students_ws.delete_rows(row_number)

    return {"message": "Student deleted successfully"}