from homeassistant.core import callback, HomeAssistant
from homeassistant.components.light import (
    LightEntity,
    LightEntityDescription,
    ATTR_BRIGHTNESS,
    ColorMode
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    ranged_value_to_percentage,
    percentage_to_ranged_value
)

from aiodirigera.device import Light
from aiodirigera.hub import Hub

from .const import DOMAIN, CONF_HUB_ID, BRIGHTNESS_SCALE
from .entity import IkeaDirigeraToggleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    hub_id: str = entry.data[CONF_HUB_ID]
    hub: Hub = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_light(light: Light):
        light = IkeaDirigeraLightEntity(hub_id, hub, light)
        async_add_entities([light])

    devices = await hub.get_devices()
    [
        async_add_light(device)
        for device in devices
        if type(device) is Light
    ]


class IkeaDirigeraLightEntity(IkeaDirigeraToggleEntity, LightEntity):
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = [ColorMode.ONOFF, ColorMode.BRIGHTNESS]

    @property
    def entity_description(self) -> LightEntityDescription:
        return LightEntityDescription(
            key="ikea_dirigera_light",
            has_entity_name=True,
            name=None
        )

    @property
    def brightness(self) -> int:
        return percentage_to_ranged_value(BRIGHTNESS_SCALE, self._delegate.brightness)

    async def async_turn_on(self, **kwargs) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            await self._delegate.set_brightness(
                ranged_value_to_percentage(
                    BRIGHTNESS_SCALE,
                    kwargs[ATTR_BRIGHTNESS]
                )
            )

        await self._delegate.turn_on()
