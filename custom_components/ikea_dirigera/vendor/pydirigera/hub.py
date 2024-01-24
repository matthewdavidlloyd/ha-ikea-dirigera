import logging
from typing import Any, Dict, List

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)

class HubAPI:

    _http_base_url: str
    _token: str

    def __init__(self, ip_address: str, token: str,) -> None:
        self._http_base_url = f"https://{ip_address}:8443/v1"
        self._token = token

    # Hub Methods

    async def get_hub_status(self) -> Dict[str, Any]:
        url = f"{self._http_base_url}/hub/status"
        return await self._get(url)

    # Device Methods
    
    async def get_devices(self) -> List[Dict]:
        url = f"{self._http_base_url}/devices"
        return await self._get(url)

    async def get_device_status(self, device_id: str) -> Dict:
        url = f"{self._http_base_url}/devices/{device_id}"
        return await self._get(url)

    async def update_device_status(self, device_id: str, data: Dict) -> Dict:
        url = f"{self._http_base_url}/devices/{device_id}"
        return await self._patch(url, data)

    # HTTP Helpers

    async def _get(self, url: str) -> Any:
        _LOGGER.debug("GET %s", url)
        client_session = ClientSession()
        try:
            async with client_session.get(url, headers=self._headers(), ssl=False, timeout=30) as res:
                res.raise_for_status()
                return await res.json()
        finally:
            await client_session.close()

    async def _patch(self, url: str, json: Dict) -> None:
        _LOGGER.debug("PATCH %s", url)
        client_session = ClientSession()
        try:
            async with client_session.patch(url, json=json, headers=self._headers(), ssl=False, timeout=30) as res:
                res.raise_for_status()
        finally:
            await client_session.close()

    def _headers(self) -> Dict[str, Any]:
        return {"Authorization": f"Bearer {self._token}"}
