from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import require_permission
from app.integrations.glpi_client import GlpiClient


router = APIRouter(tags=["glpi"])

logger = logging.getLogger(__name__)


def _norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s


def _dropdown_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("completename", "name", "value", "text"):
            v = value.get(key)
            if isinstance(v, str) and v.strip():
                return v
        return ""
    return str(value)


def _ticket_status_is_open(status: Any) -> bool:
    # GLPI: New=1, Assigned=2, Planned=3, Waiting=4, Solved=5, Closed=6
    try:
        s = int(status)
        return 1 <= s <= 4
    except Exception:
        # Se vier string, tenta algo aproximado
        st = _norm(str(status))
        return st in {"new", "assigned", "planned", "waiting"}


@router.get("/api/glpi/tickets/open")
async def list_open_tickets(
    limit: int = Query(20, ge=1, le=20),
    category: str = Query("computador"),
    _user=Depends(require_permission("add_maintenance")),
) -> Dict[str, Any]:
    """Lista tickets abertos para seleção no registro de manutenção.

    Retorna somente campos essenciais: id (número) e título.
    """
    glpi = GlpiClient()
    try:
        # Busca um pouco mais para aumentar a chance de pegar os mais recentes,
        # mas retorna somente os últimos `limit`.
        tickets = await glpi.get_open_tickets(limit=max(200, limit))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao consultar GLPI: {e}")

    try:
        raw_ids = []
        for t in tickets[-3:]:
            if isinstance(t, dict):
                raw_ids.append({"id": t.get("id"), "status": t.get("status"), "cat": _dropdown_str(t.get("itilcategories_id"))})
        logger.info("GLPI raw last 3 tickets (id/status/cat): %s", raw_ids)
    except Exception:
        pass

    wanted_cat = _norm(category)

    items: List[Dict[str, Any]] = []
    for t in tickets:
        if not isinstance(t, dict):
            continue

        if not _ticket_status_is_open(t.get("status")):
            continue

        cat_raw = t.get("itilcategories_id")
        cat_name = _norm(_dropdown_str(cat_raw))
        if wanted_cat and cat_name and wanted_cat not in cat_name:
            continue

        ticket_id = t.get("id")
        try:
            ticket_id_int = int(ticket_id)
        except Exception:
            continue
        if ticket_id_int <= 0:
            continue

        title = t.get("name") or t.get("title") or t.get("subject") or ""
        title = str(title).strip()

        items.append({"id": ticket_id_int, "title": title})

    # Ordena por id desc (mais recentes primeiro)
    items.sort(key=lambda x: x.get("id", 0), reverse=True)
    items = items[:limit]

    try:
        logger.info("GLPI filtered tickets (showing up to 3): %s", items[:3])
    except Exception:
        pass

    return {"items": items, "total": len(items)}
