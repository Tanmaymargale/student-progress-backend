import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ✅ Load credentials from Render environment variable
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    service_account_info,
    scope
)

client = gspread.authorize(creds)

sheet = client.open("Project_Progress_Management")

students_ws = sheet.worksheet("students")
batches_ws = sheet.worksheet("batches")
assignment_ws = sheet.worksheet("assignment")
contest_ws = sheet.worksheet("coding contest")
mock_ws = sheet.worksheet("mock interview")