from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_TOKEN
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.device_registry as dr

from aiodirigera.hub import Hub

from .const import DOMAIN, PLATFORMS, CONF_HUB_ID


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hub = Hub(entry.data[CONF_IP_ADDRESS], entry.data[CONF_TOKEN])
    hub_status = await hub.get_status()

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections=set(),
        identifiers={(DOMAIN, entry.data[CONF_HUB_ID])},
        manufacturer=hub_status["attributes"]["manufacturer"],
        name=hub_status["attributes"]["customName"],
        model=hub_status["attributes"]["model"],
        sw_version=hub_status["attributes"]["firmwareVersion"],
    )

    hass.data[DOMAIN][entry.entry_id] = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
