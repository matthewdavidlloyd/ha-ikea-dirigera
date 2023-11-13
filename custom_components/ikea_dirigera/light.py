import logging
from typing import Dict, List

from homeassistant.core import callback, HomeAssistant
from homeassistant.components.light import LightEntity, LightEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .vendor.pydirigera.hub import Hub as HubAPI
from .vendor.pydirigera.light import Light as LightAPI

from .const import DOMAIN, CONF_HUB_ID

_LOGGER = logging.getLogger(__name__)

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
                    is_on=device_detail["attributes"]["isOn"]
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

        self._hub_id = hub_id
        self._id = id
        self._is_on = is_on

        self._api = LightAPI(id, hub_api)

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self) -> None:
        if self._is_on:
            return

        await self._api.set_light(True)
        self._is_on = True

    async def async_turn_off(self) -> None:
        if not self._is_on:
            return

        await self._api.set_light(False)
        self._is_on = False
