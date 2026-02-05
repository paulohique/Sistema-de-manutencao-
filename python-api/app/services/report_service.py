from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Computer, MaintenanceHistory
from app.schemas.report_schemas import MaintenanceReportResponse, MaintenanceReportRow


def _dt_start(d: date) -> datetime:
    return datetime.combine(d, time.min)


def _dt_end(d: date) -> datetime:
    # inclusive end-of-day
    return datetime.combine(d, time.max)


def get_maintenance_report(
    db: Session,
    *,
    from_date: Optional[date],
    to_date: Optional[date],
    maintenance_type: Optional[str],
) -> MaintenanceReportResponse:
    query = (
        db.query(MaintenanceHistory, Computer)
        .join(Computer, Computer.id == MaintenanceHistory.computer_id)
    )

    if from_date is not None:
        query = query.filter(MaintenanceHistory.performed_at >= _dt_start(from_date))

    if to_date is not None:
        query = query.filter(MaintenanceHistory.performed_at <= _dt_end(to_date))

    if maintenance_type and maintenance_type in {"Preventiva", "Corretiva"}:
        query = query.filter(MaintenanceHistory.maintenance_type == maintenance_type)

    query = query.order_by(desc(MaintenanceHistory.performed_at))

    rows = query.all()

    items = [
        MaintenanceReportRow(
            computer_id=computer.id,
            computer_name=computer.name,
            patrimonio=computer.patrimonio,
            technician=mh.technician,
            maintenance_type=mh.maintenance_type,
            performed_at=mh.performed_at,
        )
        for (mh, computer) in rows
    ]

    return MaintenanceReportResponse(items=items, total=len(items))
