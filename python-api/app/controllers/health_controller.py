from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GLPI Manutenções API",
        "timestamp": datetime.utcnow().isoformat(),
    }
