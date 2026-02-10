from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_permission
from app.integrations.glpi_client import GlpiClient

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
    user=Depends(require_permission("add_maintenance")),
):
    # Sempre atribui o técnico ao usuário autenticado.
    # Ignora qualquer valor enviado pelo cliente para evitar spoofing.
    technician = (user.get("display_name") or user.get("sub") or "").strip() or None
    if technician:
        try:
            maintenance.technician = technician  # pydantic mutável na prática (v1/v2 default)
        except Exception:
            # fallback para modelos imutáveis (caso alterem config)
            if hasattr(maintenance, "model_copy"):
                maintenance = maintenance.model_copy(update={"technician": technician})
            else:
                maintenance = maintenance.copy(update={"technician": technician})

    created = create_maintenance(db, maintenance)
    if not created:
        raise HTTPException(status_code=404, detail="Computador não encontrado")

    # Best-effort: comenta no chamado vinculado.
    try:
        glpi = GlpiClient()
        msg_type = "preditiva" if created.maintenance_type == "Preventiva" else "corretiva"

        base_msg = f"Manutenção {msg_type} feita no devido computador"

        # Para manutenção corretiva, inclui também o texto digitado em Observação/Descrição.
        extra = ""
        if msg_type == "corretiva":
            desc = (maintenance.description or "").strip()
            if desc:
                extra = f"\n\nObservação registrada:\n{desc}"

        await glpi.add_ticket_followup(int(maintenance.glpi_ticket_id), base_msg + extra)
    except Exception:
        # Não falha o registro local caso o GLPI esteja indisponível.
        pass

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
