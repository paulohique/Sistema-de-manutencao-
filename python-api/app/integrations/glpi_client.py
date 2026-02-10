from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class GlpiClient:
    def __init__(self):
        self.base_url = settings.GLPI_BASE_URL
        self.app_token = settings.GLPI_APP_TOKEN
        self.user_token = settings.GLPI_USER_TOKEN
        self.session_token: Optional[str] = None

    async def _get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        """Requisição GET ao GLPI."""
        if not self.session_token and not path.endswith("/initSession"):
            await self.init_session()

        headers: Dict[str, str] = {"App-Token": self.app_token}
        if path.endswith("/initSession"):
            headers["Authorization"] = f"user_token {self.user_token}"
        else:
            headers["Session-Token"] = str(self.session_token)

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{path}", headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def _post(self, path: str, *, json: Optional[Dict[str, Any]] = None) -> Any:
        """Requisição POST ao GLPI.

        Observação: originalmente a integração era somente-leitura. Este método existe
        para suportar casos de uso explícitos (ex.: adicionar followup em Ticket).
        """
        if not self.session_token:
            await self.init_session()

        headers: Dict[str, str] = {
            "App-Token": self.app_token,
            "Session-Token": str(self.session_token),
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}{path}", headers=headers, json=json)
            response.raise_for_status()
            if not response.content:
                return None
            try:
                return response.json()
            except Exception:
                return response.text

    async def init_session(self) -> str:
        """Inicializa sessão com GLPI API"""
        data = await self._get("/initSession")
        self.session_token = data.get("session_token")
        return self.session_token

    async def kill_session(self):
        """Encerra sessão com GLPI API"""
        if not self.session_token:
            return

        try:
            await self._get("/killSession")
        finally:
            self.session_token = None

    async def get_computers(self, start: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca lista de computadores"""
        data = await self._get(
            "/Computer",
            params={
                "range": f"{start}-{start + limit - 1}",
                "expand_dropdowns": "true",
            },
        )
        return data if isinstance(data, list) else []

    async def get_open_tickets(self, *, limit: int = 200) -> List[Dict[str, Any]]:
        """Busca tickets abertos (best-effort).

        A API do GLPI não tem um filtro universal simples via /Ticket; por isso buscamos
        um range inicial e filtramos em memória.
        """
        limit = max(1, min(int(limit), 500))

        base_params: Dict[str, Any] = {
            "range": f"0-{limit - 1}",
            "expand_dropdowns": "true",
        }

        # GLPI normalmente suporta sort/order; isso permite pegar os tickets mais recentes.
        # Se a instalação não suportar, faz fallback para o comportamento anterior.
        try:
            data = await self._get(
                "/Ticket",
                params={
                    **base_params,
                    "sort": "id",
                    "order": "DESC",
                },
            )
        except Exception:
            data = await self._get("/Ticket", params=base_params)

        return data if isinstance(data, list) else []

    async def add_ticket_followup(self, ticket_id: int, content: str) -> None:
        """Adiciona um followup/comentário em um ticket (best-effort)."""
        ticket_id = int(ticket_id)
        content = (content or "").strip()
        if ticket_id <= 0 or not content:
            return

        # Prefer: criar ITILFollowup diretamente (formato mais comum nas versões atuais)
        payload_a = {
            "input": {
                "itemtype": "Ticket",
                "items_id": ticket_id,
                "content": content,
            }
        }

        try:
            await self._post("/ITILFollowup", json=payload_a)
            return
        except httpx.HTTPStatusError:
            pass

        # Fallback: endpoint aninhado no ticket (algumas instalações usam essa rota)
        payload_b = {"input": {"content": content}}
        try:
            await self._post(f"/Ticket/{ticket_id}/ITILFollowup", json=payload_b)
        except httpx.HTTPStatusError:
            # Último fallback: alguns GLPIs expõem /TicketFollowup
            try:
                await self._post(f"/Ticket/{ticket_id}/TicketFollowup", json=payload_b)
            except httpx.HTTPStatusError:
                return

    async def get_computer(self, computer_id: int) -> Dict[str, Any]:
        """Busca detalhes de um computador"""
        data = await self._get(
            f"/Computer/{computer_id}",
            params={"expand_dropdowns": "true"},
        )
        return data if isinstance(data, dict) else {}

    async def get_computer_items(self, computer_id: int, item_type: str) -> List[Dict[str, Any]]:
        """Busca itens relacionados ao computador."""
        try:
            data = await self._get(
                f"/Computer/{computer_id}/{item_type}",
                params={"expand_dropdowns": "true"},
            )
            return data if isinstance(data, list) else []
        except httpx.HTTPStatusError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return []
            raise

    async def get_all_components(self, computer_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Busca todos os componentes de hardware do computador"""
        component_types = [
            "Item_DeviceProcessor",
            "Item_DeviceMemory",
            "Item_DeviceHardDrive",
            "Item_DeviceNetworkCard",
            "Item_DeviceGraphicCard",
            "Item_DeviceMotherboard",
            "Item_DevicePowerSupply",
        ]

        components: Dict[str, List[Dict[str, Any]]] = {}
        for comp_type in component_types:
            try:
                items = await self.get_computer_items(computer_id, comp_type)
                if items:
                    components[comp_type] = items
            except Exception as e:
                print(f"Erro ao buscar {comp_type}: {e}")
                continue

        return components
