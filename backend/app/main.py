"""
main.py — LeadFlow API entrypoint.

Run with: uvicorn app.main:app --reload --port 8000
"""

import os
import logging
import traceback

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import auth, users, public, leads

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="LeadFlow API",
    description="Lead management API for a small sales team — Digital Heroes Full Stack Development, Task A.",
    version="1.0.0",
)

# Comma-separated list of allowed frontend origins, e.g.
# "http://localhost:5173,https://leadflow.vercel.app"
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(leads.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"Unhandled exception on {request.method} {request.url.path}:\n{tb}")
    response = JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)}"},
    )
    origin = request.headers.get("origin")
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "LeadFlow API"}
