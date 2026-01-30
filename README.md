# Student Progress Management Backend

This is the backend for **Student Progress Management System**, built using **FastAPI** and **Google Sheets** as the database.

---

## Features

- CRUD operations for:
  - Students
  - Batches
  - Assignments
  - Coding Contests
  - Mock Interviews
- Placement readiness evaluation
- Google Sheets integration via `gspread`

---

## Project Structure
backend/
│
├── main.py # FastAPI app
├── sheets.py # Google Sheets connections
├── routes/ # API routes
│ ├── students.py
│ ├── batches.py
│ ├── assignments.py
│ ├── contests.py
│ ├── mocks.py
│ └── placement.py
├── myenv/ # Python virtual environment (ignored in Git)
└── service_account.json # Google Sheets service account (ignored in Git)

