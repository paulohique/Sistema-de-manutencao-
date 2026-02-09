from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_permission

# Auth temporariamente desabilitada para rotas de escrita (manutenção).
# Para reativar no futuro, reintroduza `Depends(get_current_user)` nas rotas POST/PUT/DELETE.
from app.core.database import get_db
from app.schemas.schemas import MaintenanceCreate, MaintenanceOut, MaintenanceUpdate
from app.services.maintenance_service import create_maintenance, delete_maintenance, update_maintenance


router = APIRouter(tags=["maintenance"])


@router.post("/api/maintenance", response_model=MaintenanceOut)
async def create_maintenance_endpoint(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("add_maintenance")),
):
    created = create_maintenance(db, maintenance)
    if not created:
        raise HTTPException(status_code=404, detail="Computador não encontrado")
    return created


@router.put("/api/maintenance/{maintenance_id}", response_model=MaintenanceOut)
async def update_maintenance_endpoint(
    maintenance_id: int,
    payload: MaintenanceUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("add_maintenance")),
):
    updated = update_maintenance(db, maintenance_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    return updated


@router.delete("/api/maintenance/{maintenance_id}")
async def delete_maintenance_endpoint(
    maintenance_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_permission("add_maintenance")),
):
    deleted = delete_maintenance(db, maintenance_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    return {"status": "deleted"}
