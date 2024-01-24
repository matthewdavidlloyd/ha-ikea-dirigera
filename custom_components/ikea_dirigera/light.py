import logging

from homeassistant.core import callback, HomeAssistant
from homeassistant.components.light import LightEntity, LightEntityDescription, ATTR_BRIGHTNESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import ranged_value_to_percentage, percentage_to_ranged_value

from .vendor.pydirigera.device import DeviceAPI, LightAPI
from .vendor.pydirigera.hub import HubAPI

from .const import DOMAIN, CONF_HUB_ID, BRIGHTNESS_SCALE
from .entity import IkeaDirigeraEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    hub_id: str = entry.data[CONF_HUB_ID]
    hub_api: HubAPI = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_light(device_id: str, device_info: DeviceInfo):
        light = IkeaDirigeraLightEntity(hub_api, device_id, device_info)
        async_add_entities([light])

    device_details = await hub_api.get_devices()
    for device_detail in device_details:
        device_type = device_detail["deviceType"]
        if device_type == "light":
            device_id = device_detail["id"]
            device_info = DeviceInfo(
                identifiers={
                    (DOMAIN, device_id)
                },
                via_device=(DOMAIN, hub_id),
                manufacturer=device_detail["attributes"]["manufacturer"],
                model=device_detail["attributes"]["model"],
                serial_number=device_detail["attributes"]["serialNumber"],
                name=device_detail["attributes"]["customName"],
                sw_version=device_detail["attributes"]["firmwareVersion"],
            )
            async_add_light(device_id, device_info)


class IkeaDirigeraLightEntity(IkeaDirigeraEntity, LightEntity):
    entity_description = LightEntityDescription(
        key="ikea_dirigera_light",
        has_entity_name=True,
        name=None
    )

    _api: LightAPI

    def __init__(self, hub_api: HubAPI, id: str, device_info: DeviceInfo):
        super().__init__(id, device_info)
        self._api = LightAPI(hub_api, id)

    async def async_turn_on(self, **kwargs) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            brightness_percentage = ranged_value_to_percentage(BRIGHTNESS_SCALE, brightness)
            await self._api.set_light_level(brightness_percentage)
            self._attr_brightness = brightness

        if self._attr_is_on:
            return

        await self._api.turn_on()
        self._attr_is_on = True

    async def async_turn_off(self) -> None:
        if not self._attr_is_on:
            return

        await self._api.turn_off()
        self._attr_is_on = False

    async def async_update(self) -> None:
        status = await self._api.get_status()
        self._attr_is_on = status["attributes"]["isOn"]
        self._attr_brightness = percentage_to_ranged_value(BRIGHTNESS_SCALE, status["attributes"]["lightLevel"])
    