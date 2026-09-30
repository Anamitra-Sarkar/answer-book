from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api import api_router

app = FastAPI(title="Answer book API",
              description="REST API for Exam Paper Ingestion and automated LangGraph Question Solving",
              version= "1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive API documentation"""
    return RedirectResponse(url= "/docs")

