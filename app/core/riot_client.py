from typing import Any, Dict

import httpx

from app.core.config import get_settings


class RiotClient:
    """Cliente simple para la API de Riot Games.

    Aquí puedes ir agregando métodos específicos para:
    - Obtener partidas
    - Obtener info de campeones
    - Etc.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = f"https://{self.settings.riot_region}.api.riotgames.com"
        self.api_key = self.settings.riot_api_key

    async def _get(self, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        headers = {"X-Riot-Token": self.api_key}
        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_match(self, match_id: str) -> Dict[str, Any]:
        """Ejemplo: obtener datos de una partida concreta."""
        path = f"/lol/match/v5/matches/{match_id}"
        return await self._get(path)
