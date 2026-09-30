from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Health check endpoint to verify API service status."""
    return {
        "status": "ok",
        "service": "AnswerBook API",
        "version": "1.0.0"
    }