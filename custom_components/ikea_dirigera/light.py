import logging
from typing import Dict, List

from homeassistant.core import callback, HomeAssistant
from homeassistant.components.light import LightEntity, LightEntityDescription, ColorMode, ATTR_BRIGHTNESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import ranged_value_to_percentage, percentage_to_ranged_value

from .vendor.pydirigera.hub import Hub as HubAPI
from .vendor.pydirigera.light import Light as LightAPI

from .const import DOMAIN, CONF_HUB_ID

_LOGGER = logging.getLogger(__name__)

BRIGHTNESS_SCALE = (1, 255)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    hub_api: HubAPI = hass.data[DOMAIN][entry.entry_id]
    hub_id: str = entry.data[CONF_HUB_ID]

    @callback
    def async_add_light(device_detail: Dict):
        light = IkeaDirigeraLightEntity(
                    hub_id=hub_id,
                    hub_api=hub_api,
                    id=device_detail["id"],
                    manufacturer=device_detail["attributes"]["manufacturer"],
                    model=device_detail["attributes"]["model"],
                    serial_number=device_detail["attributes"]["serialNumber"],
                    name=device_detail["attributes"]["customName"],
                    sw_version=device_detail["attributes"]["firmwareVersion"],
                    is_on=device_detail["attributes"]["isOn"],
                    brightness=percentage_to_ranged_value(BRIGHTNESS_SCALE, device_detail["attributes"]["lightLevel"])
                )
        async_add_entities([light])

    device_details = await hub_api.get_devices()
    for device_detail in device_details:
        if device_detail["type"] == "light":
            async_add_light(device_detail)

class IkeaDirigeraLightEntity(LightEntity):

    _hub_id: str
    _id: str

    _is_on: bool
    _brightness: int

    _api: LightAPI

    entity_description = LightEntityDescription(
        key="ikea_dirigera_light",
        has_entity_name=True,
        name=None
    )

    def __init__(
            self,
            hub_id: str,
            id: str,
            manufacturer: str,
            model: str,
            serial_number: str,
            name: str,
            sw_version: str,
            is_on: bool,
            brightness: int,
            hub_api: HubAPI,
    ):
        self._attr_unique_id = serial_number
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, self.unique_id)
            },
            via_device=(DOMAIN, hub_id),
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            name=name,
            sw_version=sw_version,
        )
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

        self._hub_id = hub_id
        self._id = id
        
        self._is_on = is_on
        self._brightness = brightness

        self._api = LightAPI(id, hub_api)

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        _LOGGER.debug("async_turn_on for %s with kwargs %s", self._id, kwargs)
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            brightness_percentage = ranged_value_to_percentage(BRIGHTNESS_SCALE, brightness)
            await self._api.set_light_level(brightness_percentage)
            self._attr_brightness = brightness

        if self._is_on:
            return

        await self._api.turn_on()
        self._is_on = True

    async def async_turn_off(self) -> None:
        if not self._is_on:
            return

        await self._api.turn_off()
        self._is_on = False

    async def async_update(self) -> None:
        await self._update_state()

    async def _update_state(self) -> None:
        # TODO: do a single call per-hub and keep state in there instead
        status = await self._api.get_status()
        self._is_on = status["attributes"]["isOn"]
        self._attr_brightness = percentage_to_ranged_value(BRIGHTNESS_SCALE, status["attributes"]["lightLevel"])
