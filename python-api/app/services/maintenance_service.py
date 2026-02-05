from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Computer, MaintenanceHistory
from typing import Optional

from app.schemas.schemas import MaintenanceCreate, MaintenanceUpdate


def create_maintenance(db: Session, maintenance: MaintenanceCreate) -> Optional[MaintenanceHistory]:
    computer = db.query(Computer).filter(Computer.id == maintenance.computer_id).first()
    if not computer:
        return None

    next_due = None
    if maintenance.maintenance_type == "Preventiva" and maintenance.next_due_days:
        next_due = maintenance.performed_at + timedelta(days=maintenance.next_due_days)

    maintenance_record = MaintenanceHistory(
        computer_id=maintenance.computer_id,
        maintenance_type=maintenance.maintenance_type,
        description=maintenance.description,
        performed_at=maintenance.performed_at,
        technician=maintenance.technician,
        next_due=next_due,
    )
    db.add(maintenance_record)

    computer.last_maintenance = maintenance.performed_at
    computer.next_maintenance = next_due

    db.commit()
    db.refresh(maintenance_record)
    return maintenance_record


def get_device_maintenance_history(db: Session, device_id: int):
    return (
        db.query(MaintenanceHistory)
        .filter(MaintenanceHistory.computer_id == device_id)
        .order_by(desc(MaintenanceHistory.performed_at))
        .all()
    )


def update_maintenance(db: Session, maintenance_id: int, payload: MaintenanceUpdate) -> Optional[MaintenanceHistory]:
    record = db.query(MaintenanceHistory).filter(MaintenanceHistory.id == maintenance_id).first()
    if not record:
        return None

    if payload.maintenance_type is not None:
        record.maintenance_type = payload.maintenance_type
    if payload.description is not None:
        record.description = payload.description
    if payload.performed_at is not None:
        record.performed_at = payload.performed_at
    if payload.technician is not None:
        record.technician = payload.technician

    next_due = record.next_due
    if record.maintenance_type == "Preventiva" and payload.next_due_days is not None:
        next_due = record.performed_at + timedelta(days=payload.next_due_days)
    if record.maintenance_type != "Preventiva":
        next_due = None
    record.next_due = next_due
    record.updated_at = datetime.utcnow()

    computer = db.query(Computer).filter(Computer.id == record.computer_id).first()
    if computer:
        computer.last_maintenance = record.performed_at
        computer.next_maintenance = next_due
        computer.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(record)
    return record


def delete_maintenance(db: Session, maintenance_id: int) -> Optional[int]:
    record = db.query(MaintenanceHistory).filter(MaintenanceHistory.id == maintenance_id).first()
    if not record:
        return None

    computer_id = record.computer_id
    db.delete(record)
    db.commit()

    computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if computer:
        latest = (
            db.query(MaintenanceHistory)
            .filter(MaintenanceHistory.computer_id == computer_id)
            .order_by(desc(MaintenanceHistory.performed_at))
            .first()
        )
        if latest:
            computer.last_maintenance = latest.performed_at
            computer.next_maintenance = latest.next_due
        else:
            computer.last_maintenance = None
            computer.next_maintenance = None
        computer.updated_at = datetime.utcnow()
        db.commit()

    return computer_id
