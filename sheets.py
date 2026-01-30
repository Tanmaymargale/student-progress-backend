import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Absolute path
base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, "service_account.json")

creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)

sheet = client.open("Project_Progress_Management")
students_ws = sheet.worksheet("students")
batches_ws = sheet.worksheet("batches")
assignment_ws = sheet.worksheet("assignment")
contest_ws = sheet.worksheet("coding contest")
mock_ws = sheet.worksheet("mock interview")
