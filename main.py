from fastapi import FastAPI
from routes import students, batches, assignments, contests, mocks, placement

app = FastAPI(title="Student Progress Management")

app.include_router(students, prefix="/students", tags=["Students"])
app.include_router(batches, prefix="/batches", tags=["Batches"])
app.include_router(assignments, prefix="/assignments", tags=["Assignments"])
app.include_router(contests, prefix="/contests", tags=["Coding Contests"])
app.include_router(mocks, prefix="/mocks", tags=["Mock Interviews"])
app.include_router(placement, prefix="/placement", tags=["Placement"])
