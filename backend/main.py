"""
Jyotisha — Precision Vedic Astrology Application
FastAPI entry point with CORS middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router

app = FastAPI(
    title="Jyotisha — Precision Vedic Astrology API",
    description="NASA JPL DE440 ephemeris-backed Vedic astrology calculations with IEEE 754 float64 precision.",
    version="1.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Jyotisha API",
        "version": "1.6.0",
        "precision": "IEEE 754 float64",
        "ephemeris": "NASA JPL DE440",
    }
