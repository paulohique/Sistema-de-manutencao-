import httpx
from typing import Optional, Dict, Any, List
from config import settings

class GlpiClient:
    def __init__(self):
        self.base_url = settings.GLPI_BASE_URL
        self.app_token = settings.GLPI_APP_TOKEN
        self.user_token = settings.GLPI_USER_TOKEN
        self.session_token: Optional[str] = None
    
    async def init_session(self) -> str:
        """Inicializa sessão com GLPI API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/initSession",
                headers={
                    "App-Token": self.app_token,
                    "Authorization": f"user_token {self.user_token}"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.session_token = data.get("session_token")
            return self.session_token
    
    async def kill_session(self):
        """Encerra sessão com GLPI API"""
        if not self.session_token:
            return
        
        async with httpx.AsyncClient() as client:
            await client.get(
                f"{self.base_url}/killSession",
                headers={
                    "App-Token": self.app_token,
                    "Session-Token": self.session_token
                }
            )
            self.session_token = None
    
    async def get_computers(self, start: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca lista de computadores"""
        if not self.session_token:
            await self.init_session()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/Computer",
                headers={
                    "App-Token": self.app_token,
                    "Session-Token": self.session_token
                },
                params={
                    "range": f"{start}-{start + limit - 1}",
                    "expand_dropdowns": "true"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_computer(self, computer_id: int) -> Dict[str, Any]:
        """Busca detalhes de um computador"""
        if not self.session_token:
            await self.init_session()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/Computer/{computer_id}",
                headers={
                    "App-Token": self.app_token,
                    "Session-Token": self.session_token
                },
                params={"expand_dropdowns": "true"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_computer_items(self, computer_id: int, item_type: str) -> List[Dict[str, Any]]:
        """
        Busca itens relacionados ao computador (componentes, discos, etc)
        item_type: Item_DeviceProcessor, Item_DeviceMemory, Item_DeviceHardDrive, etc
        """
        if not self.session_token:
            await self.init_session()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/Computer/{computer_id}/{item_type}",
                headers={
                    "App-Token": self.app_token,
                    "Session-Token": self.session_token
                },
                params={"expand_dropdowns": "true"}
            )
            
            if response.status_code == 404:
                return []
            
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
    
    async def get_all_components(self, computer_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Busca todos os componentes de hardware do computador"""
        component_types = [
            "Item_DeviceProcessor",      # CPU
            "Item_DeviceMemory",          # RAM
            "Item_DeviceHardDrive",       # HD/SSD
            "Item_DeviceNetworkCard",     # Placa de Rede
            "Item_DeviceGraphicCard",     # Placa de Vídeo
            "Item_DeviceMotherboard",     # Placa Mãe
            "Item_DevicePowerSupply",     # Fonte
        ]
        
        components = {}
        for comp_type in component_types:
            try:
                items = await self.get_computer_items(computer_id, comp_type)
                if items:
                    components[comp_type] = items
            except Exception as e:
                print(f"Erro ao buscar {comp_type}: {e}")
                continue
        
        return components
