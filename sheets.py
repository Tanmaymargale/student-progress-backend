import os
import json
import gspread
from google.oauth2.service_account import Credentials

# -------------------------
# Scope
# -------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# -------------------------
# Load credentials from environment variable
# -------------------------
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scope
)

# -------------------------
# Connect to Google Sheets
# -------------------------
client = gspread.authorize(creds)

sheet = client.open("Project_Progress_Management")

students_ws = sheet.worksheet("students")
batches_ws = sheet.worksheet("batches")
assignment_ws = sheet.worksheet("assignment")
contest_ws = sheet.worksheet("coding contest")
mock_ws = sheet.worksheet("mock interview")