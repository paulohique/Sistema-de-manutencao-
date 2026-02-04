from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from database import engine, get_db, Base
from models import Computer, ComputerComponent, MaintenanceHistory, ComputerNote
from schemas import (
    ComputerOut, ComponentOut, MaintenanceCreate, MaintenanceOut,
    NoteCreate, NoteOut, DevicesPage, DeviceRow, DeviceDetail, SyncResult
)
from glpi_client import GlpiClient
from config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GLPI Manutenções API",
    description="API para gerenciamento de manutenção de computadores integrada ao GLPI",
    version="1.0.0"
)

# CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== SYNC GLPI ====================

@app.post("/api/sync/glpi", response_model=SyncResult)
async def sync_glpi_computers(db: Session = Depends(get_db)):
    """Sincroniza computadores do GLPI com o banco de dados local"""
    glpi = GlpiClient()
    computers_synced = 0
    components_synced = 0
    
    try:
        await glpi.init_session()
        
        # Buscar computadores do GLPI (paginação)
        start = 0
        limit = 50
        
        while True:
            computers_data = await glpi.get_computers(start=start, limit=limit)
            
            if not computers_data:
                break
            
            for comp_data in computers_data:
                glpi_id = comp_data.get("id")
                if not glpi_id:
                    continue
                
                # Verificar se computador já existe
                computer = db.query(Computer).filter(Computer.glpi_id == glpi_id).first()
                
                if not computer:
                    computer = Computer(glpi_id=glpi_id)
                    db.add(computer)
                
                # Atualizar dados
                computer.name = comp_data.get("name", f"Computer-{glpi_id}")
                computer.entity = comp_data.get("entities_id", "")
                computer.patrimonio = comp_data.get("otherserial", "")
                computer.serial = comp_data.get("serial", "")
                computer.location = comp_data.get("locations_id", "")
                computer.status = comp_data.get("states_id", "")
                computer.glpi_data = comp_data
                computer.updated_at = datetime.utcnow()
                
                computers_synced += 1
                
                # Buscar componentes
                try:
                    components = await glpi.get_all_components(glpi_id)
                    
                    # Limpar componentes antigos
                    db.query(ComputerComponent).filter(
                        ComputerComponent.computer_id == computer.id
                    ).delete()
                    
                    # Adicionar novos componentes
                    for comp_type, items in components.items():
                        for item in items:
                            component = ComputerComponent(
                                computer_id=computer.id,
                                component_type=comp_type.replace("Item_Device", ""),
                                name=item.get("designation", ""),
                                manufacturer=item.get("manufacturers_id", ""),
                                model=item.get("devicemodels_id", ""),
                                serial=item.get("serial", ""),
                                capacity=item.get("size", ""),
                                component_data=item
                            )
                            db.add(component)
                            components_synced += 1
                
                except Exception as e:
                    logger.error(f"Erro ao sincronizar componentes do computer {glpi_id}: {e}")
            
            db.commit()
            
            # Próxima página
            if len(computers_data) < limit:
                break
            start += limit
        
        await glpi.kill_session()
        
        return SyncResult(
            computers_synced=computers_synced,
            components_synced=components_synced,
            message=f"Sincronizados {computers_synced} computadores e {components_synced} componentes"
        )
    
    except Exception as e:
        await glpi.kill_session()
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")


@app.post("/api/webhook/glpi")
async def glpi_webhook(db: Session = Depends(get_db)):
    """Webhook para sincronização automática quando há mudanças no GLPI"""
    try:
        result = await sync_glpi_computers(db)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DEVICES ====================

def calculate_maintenance_status(last_maintenance: Optional[datetime], next_maintenance: Optional[datetime]) -> str:
    """Calcula status de manutenção"""
    if not next_maintenance:
        return "Pendente"
    
    now = datetime.utcnow()
    if now > next_maintenance:
        return "Atrasada"
    
    return "Em Dia"


@app.get("/api/devices", response_model=DevicesPage)
async def list_devices(
    tab: str = Query("all", pattern="^(all|preventiva|corretiva)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista dispositivos com paginação e filtros"""
    query = db.query(Computer)
    
    # Filtro de busca
    if q:
        query = query.filter(
            or_(
                Computer.name.ilike(f"%{q}%"),
                Computer.patrimonio.ilike(f"%{q}%"),
                Computer.serial.ilike(f"%{q}%"),
                Computer.entity.ilike(f"%{q}%")
            )
        )
    
    # Filtro por tipo de manutenção
    if tab == "preventiva":
        query = query.filter(Computer.last_maintenance.isnot(None))
    elif tab == "corretiva":
        query = query.filter(
            or_(
                Computer.next_maintenance.is_(None),
                Computer.next_maintenance < datetime.utcnow()
            )
        )
    
    total = query.count()
    
    # Paginação
    offset = (page - 1) * page_size
    computers = query.order_by(desc(Computer.updated_at)).offset(offset).limit(page_size).all()
    
    # Formatar resposta
    items = []
    for comp in computers:
        status = calculate_maintenance_status(comp.last_maintenance, comp.next_maintenance)
        items.append(DeviceRow(
            id=comp.id,
            glpi_id=comp.glpi_id,
            name=comp.name,
            maintenance_status=status,
            last_maintenance=comp.last_maintenance.strftime("%Y-%m-%d") if comp.last_maintenance else None,
            next_maintenance=comp.next_maintenance.strftime("%Y-%m-%d") if comp.next_maintenance else None
        ))
    
    return DevicesPage(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


@app.get("/api/devices/{device_id}", response_model=DeviceDetail)
async def get_device_detail(device_id: int, db: Session = Depends(get_db)):
    """Busca detalhes de um dispositivo"""
    computer = db.query(Computer).filter(Computer.id == device_id).first()
    
    if not computer:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    return DeviceDetail.from_orm(computer)


# ==================== COMPONENTS ====================

@app.get("/api/devices/{device_id}/components", response_model=List[ComponentOut])
async def get_device_components(device_id: int, db: Session = Depends(get_db)):
    """Lista componentes de hardware de um dispositivo"""
    computer = db.query(Computer).filter(Computer.id == device_id).first()
    
    if not computer:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    components = db.query(ComputerComponent).filter(
        ComputerComponent.computer_id == device_id
    ).all()
    
    return components


# ==================== MAINTENANCE ====================

@app.post("/api/maintenance", response_model=MaintenanceOut)
async def create_maintenance(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    """Registra uma nova manutenção"""
    computer = db.query(Computer).filter(Computer.id == maintenance.computer_id).first()
    
    if not computer:
        raise HTTPException(status_code=404, detail="Computador não encontrado")
    
    # Calcular próxima manutenção
    next_due = None
    if maintenance.maintenance_type == "Preventiva" and maintenance.next_due_days:
        next_due = maintenance.performed_at + timedelta(days=maintenance.next_due_days)
    
    # Criar registro de manutenção
    maintenance_record = MaintenanceHistory(
        computer_id=maintenance.computer_id,
        maintenance_type=maintenance.maintenance_type,
        description=maintenance.description,
        performed_at=maintenance.performed_at,
        technician=maintenance.technician,
        next_due=next_due
    )
    
    db.add(maintenance_record)
    
    # Atualizar computador
    computer.last_maintenance = maintenance.performed_at
    if next_due:
        computer.next_maintenance = next_due
    
    db.commit()
    db.refresh(maintenance_record)
    
    return maintenance_record


@app.get("/api/devices/{device_id}/maintenance", response_model=List[MaintenanceOut])
async def get_device_maintenance_history(device_id: int, db: Session = Depends(get_db)):
    """Lista histórico de manutenções de um dispositivo"""
    computer = db.query(Computer).filter(Computer.id == device_id).first()
    
    if not computer:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    history = db.query(MaintenanceHistory).filter(
        MaintenanceHistory.computer_id == device_id
    ).order_by(desc(MaintenanceHistory.performed_at)).all()
    
    return history


# ==================== NOTES ====================

@app.get("/api/devices/{device_id}/notes", response_model=List[NoteOut])
async def get_device_notes(device_id: int, db: Session = Depends(get_db)):
    """Lista notas de um dispositivo"""
    computer = db.query(Computer).filter(Computer.id == device_id).first()
    
    if not computer:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    notes = db.query(ComputerNote).filter(
        ComputerNote.computer_id == device_id
    ).order_by(desc(ComputerNote.created_at)).all()
    
    return notes


@app.post("/api/devices/{device_id}/notes", response_model=NoteOut)
async def create_device_note(
    device_id: int,
    note: NoteCreate,
    db: Session = Depends(get_db)
):
    """Adiciona uma nota a um dispositivo"""
    computer = db.query(Computer).filter(Computer.id == device_id).first()
    
    if not computer:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    note_record = ComputerNote(
        computer_id=device_id,
        author=note.author,
        content=note.content
    )
    
    db.add(note_record)
    db.commit()
    db.refresh(note_record)
    
    return note_record


# ==================== HEALTH ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GLPI Manutenções API",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
