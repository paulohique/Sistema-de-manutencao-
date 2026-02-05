from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MaintenanceReportRow(BaseModel):
    computer_id: int
    computer_name: str
    patrimonio: Optional[str] = None
    technician: Optional[str] = None
    maintenance_type: str = Field(..., pattern="^(Preventiva|Corretiva)$")
    performed_at: datetime


class MaintenanceReportResponse(BaseModel):
    items: List[MaintenanceReportRow]
    total: int
