from typing import Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (CONF_IP_ADDRESS, CONF_TOKEN)

from aiodirigera.auth import (
    ALPHABET,
    CODE_LENGTH,
    random_code,
    send_challenge,
    get_token
)
from aiodirigera.hub import Hub

from .const import CONF_HUB_ID, DOMAIN


# TODO: Add error handling
# TODO: Unique ids: https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
class IkeaDirigeraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    _id_address: str
    _code_verfier: str
    _code: str
    _token: str

    async def async_step_user(self, info: Optional[dict] = None):
        if info is not None:
            self._ip_address = info[CONF_IP_ADDRESS]
            self._code_verifier = random_code(ALPHABET, CODE_LENGTH)
            self._code = await send_challenge(self._ip_address, self._code_verifier)
            return await self.async_step_accept_challenge()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP_ADDRESS): str})
        )

    async def async_step_accept_challenge(self, info: Optional[dict] = None):
        if info is not None:
            self._token = await get_token(self._ip_address, self._code, self._code_verifier)
            hub = Hub(self._ip_address, self._token)
            hub_status = await hub.get_status()
            hub_id = hub_status.id
            await self.async_set_unique_id(hub_id)
            self._abort_if_unique_id_configured(hub_id)

            return self.async_create_entry(
                title="Dirigera Hub",
                data={
                    CONF_IP_ADDRESS: self._ip_address,
                    CONF_HUB_ID: hub_id,
                    CONF_TOKEN: self._token,
                }
            )

        return self.async_show_form(
            step_id="accept_challenge",
        )
