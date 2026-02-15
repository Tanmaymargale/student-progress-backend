import gspread
from google.oauth2.service_account import Credentials

# 🔹 Path to your service account JSON file
SERVICE_ACCOUNT_FILE = "service_account.json"  # make sure this file is in your backend folder

# 🔹 Define the scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 🔹 Load credentials from JSON file
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

# 🔹 Authorize gspread client
client = gspread.authorize(creds)

# 🔹 Open your spreadsheet
sheet = client.open("Project_Progress_Management")

# 🔹 Access worksheets
students_ws = sheet.worksheet("students")
batches_ws = sheet.worksheet("batches")
assignment_ws = sheet.worksheet("assignment")
contest_ws = sheet.worksheet("coding contest")
mock_ws = sheet.worksheet("mock interview")