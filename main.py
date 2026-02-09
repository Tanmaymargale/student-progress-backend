from fastapi import FastAPI
from routes.students import router as students_router
from routes.batches import router as batches_router
from routes.assignments import router as assignments_router
from routes.contests import router as contests_router
from routes.mocks import router as mocks_router
from routes.placement import router as placement_router  # if placement is unchanged

app = FastAPI(title="Student Progress Management")

# Include routers
app.include_router(students_router, prefix="/students", tags=["Students"])
app.include_router(batches_router, prefix="/batches", tags=["Batches"])
app.include_router(assignments_router, prefix="/assignments", tags=["Assignments"])
app.include_router(contests_router, prefix="/contests", tags=["Coding Contests"])
app.include_router(mocks_router, prefix="/mocks", tags=["Mock Interviews"])
app.include_router(placement_router, prefix="/placement", tags=["Placement"])
