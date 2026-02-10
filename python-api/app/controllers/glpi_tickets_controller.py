from __future__ import annotations

import asyncio
import time
import logging
import re
import unicodedata
import html
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import require_permission
from app.core.config import settings
from app.integrations.glpi_client import GlpiClient


router = APIRouter(tags=["glpi"])

logger = logging.getLogger(__name__)


_tickets_cache_lock = asyncio.Lock()
_tickets_cache: Dict[str, Dict[str, Any]] = {}


def _cache_key(*, category: str, limit: int) -> str:
    return f"cat={_norm(category)}|limit={int(limit)}"


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    entry = _tickets_cache.get(key)
    if not entry:
        return None
    now = time.time()
    ttl = int(getattr(settings, "GLPI_TICKETS_CACHE_TTL_SECONDS", 30) or 30)
    stale_max = int(getattr(settings, "GLPI_TICKETS_CACHE_STALE_MAX_SECONDS", 600) or 600)
    age = now - float(entry.get("ts") or 0)
    if age <= ttl:
        return entry
    if age <= stale_max:
        # Cache expirou para refresh, mas ainda serve em caso de falha do GLPI.
        return entry
    return None


def _cache_is_fresh(entry: Dict[str, Any]) -> bool:
    now = time.time()
    ttl = int(getattr(settings, "GLPI_TICKETS_CACHE_TTL_SECONDS", 30) or 30)
    age = now - float(entry.get("ts") or 0)
    return age <= ttl


def _cache_set(key: str, payload: Dict[str, Any]) -> None:
    _tickets_cache[key] = {"ts": time.time(), **payload}


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
    cache_key = _cache_key(category=category, limit=limit)

    async with _tickets_cache_lock:
        cached = _cache_get(cache_key)

    if cached and _cache_is_fresh(cached):
        return {"items": cached.get("items") or [], "total": int(cached.get("total") or 0)}

    glpi = GlpiClient()
    try:
        # Busca um pouco mais para aumentar a chance de pegar os mais recentes,
        # mas retorna somente os últimos `limit`.
        tickets = await glpi.get_open_tickets(limit=max(200, limit))
    except Exception as e:
        if cached:
            return {"items": cached.get("items") or [], "total": int(cached.get("total") or 0)}
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
        if title:
            title = html.unescape(title)
            # Alguns títulos do GLPI vêm com separador hierárquico (ex.: "SSP > Defesa Civil").
            # Padroniza removendo o caractere '>' para não aparecer como '&#62;' ou '>'.
            title = title.replace(">", "-")
            title = re.sub(r"\s*-\s*", " - ", title)
            title = re.sub(r"\s+", " ", title).strip()

        items.append({"id": ticket_id_int, "title": title})

    # Ordena por id desc (mais recentes primeiro)
    items.sort(key=lambda x: x.get("id", 0), reverse=True)
    items = items[:limit]

    try:
        logger.info("GLPI filtered tickets (showing up to 3): %s", items[:3])
    except Exception:
        pass

    payload = {"items": items, "total": len(items)}
    async with _tickets_cache_lock:
        _cache_set(cache_key, payload)
    return payload
