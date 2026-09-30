from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.solver import router as solver_router

router = APIRouter(prefix="/v1")

router.include_router(health_router)
router.include_router(ingestion_router)
router.include_router(solver_router)