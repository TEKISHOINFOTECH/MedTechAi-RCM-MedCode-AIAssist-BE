"""
Vercel serverless function entry point for FastAPI backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import your FastAPI app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app

# Configure CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create handler for Vercel
handler = Mangum(app, lifespan="off")
