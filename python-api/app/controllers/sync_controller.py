from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.schemas import SyncResult, SyncStatus
from app.services.sync_service import (
    get_sync_status,
    is_sync_running,
    start_sync_background,
    sync_glpi_computers_impl,
)


router = APIRouter(tags=["sync"])


@router.post("/api/sync/glpi", response_model=SyncResult)
async def sync_glpi_computers(
    async_run: bool = Query(False, alias="async"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if async_run:
        if is_sync_running():
            return SyncResult(
                computers_synced=0,
                components_synced=0,
                message="Sincronização já em andamento. Consulte /api/sync/status.",
            )
        start_sync_background()
        return SyncResult(
            computers_synced=0,
            components_synced=0,
            message="Sincronização iniciada em background. Consulte /api/sync/status.",
        )

    try:
        return await sync_glpi_computers_impl(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")


@router.get("/api/sync/status", response_model=SyncStatus)
async def get_status():
    return get_sync_status()


@router.post("/api/webhook/glpi")
async def glpi_webhook(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    try:
        result = await sync_glpi_computers_impl(db)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
