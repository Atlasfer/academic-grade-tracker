from fastapi import FastAPI, Request
from routers import mahasiswa, semester, matakuliah, simulasi
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Academic Grade Tracker API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mahasiswa.router)
app.include_router(semester.router)
app.include_router(matakuliah.router)
app.include_router(simulasi.router)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )

