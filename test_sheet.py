from sheets import students_ws

# Fetch first 5 rows from the students sheet
data = students_ws.get_all_records()
for row in data[:5]:
    print(row)
