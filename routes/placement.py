from fastapi import APIRouter, HTTPException
from sheets import students_ws, assignment_ws, contest_ws, mock_ws

router = APIRouter()


# =========================
# Helper Functions
# =========================

def to_int_safe(value, default=0):
    """Convert a value to int safely, ignoring non-digit characters"""
    try:
        digits = ''.join(filter(str.isdigit, str(value)))
        return int(digits) if digits else default
    except:
        return default


def get_str_safe(value):
    """Convert a value to lowercase string safely"""
    return str(value).strip().lower() if value else ""


def student_exists(reg_id: int) -> bool:
    """Check if a student exists by registration_id"""
    return any(
        int(s.get("registration_id") or 0) == reg_id
        for s in students_ws.get_all_records()
    )


# =========================
# Placement Status Endpoint
# =========================

@router.get("/{registration_id}")
def placement_status(registration_id: int):
    if not student_exists(registration_id):
        raise HTTPException(status_code=404, detail="Student not found")

    # Assignments
    assignments = [
        a for a in assignment_ws.get_all_records()
        if to_int_safe(a.get("registration_id")) == registration_id
    ]
    avg_marks = (
        sum(to_int_safe(a.get("marks")) for a in assignments) / len(assignments)
        if assignments else 0
    )

    # Contests
    contests = [
        c for c in contest_ws.get_all_records()
        if to_int_safe(c.get("registration_id")) == registration_id
    ]
    contest_ok = any(
        to_int_safe(c.get("score")) >= 50 and to_int_safe(c.get("rank")) <= 10
        for c in contests
    )

    # Mock Interviews
    mocks = [
        m for m in mock_ws.get_all_records()
        if to_int_safe(m.get("registration_id")) == registration_id
    ]
    mock_ok = any(
        to_int_safe(m.get("score")) >= 60 and get_str_safe(m.get("status")) == "pass"
        for m in mocks
    )

    placement_ready = avg_marks >= 40 and contest_ok and mock_ok

    return {
        "registration_id": registration_id,
        "average_assignment_marks": avg_marks,
        "coding_contest_pass": contest_ok,
        "mock_interview_pass": mock_ok,
        "placement_ready": "Yes" if placement_ready else "No"
    }
