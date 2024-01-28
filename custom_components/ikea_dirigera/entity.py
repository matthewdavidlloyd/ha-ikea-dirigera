from homeassistant.helpers.device_registry import DeviceInfo

from aiodirigera.device import Device
from aiodirigera.hub import Hub

from .const import DOMAIN


class IkeaDirigeraEntity:
    _hub_id: str
    _hub: Hub
    _delegate: Device

    def __init__(self, hub_id: str, hub: Hub, device: Device):
        self._hub_id = hub_id
        self._hub = hub
        self._delegate = device

    @property
    def unique_id(self) -> str:
        return self._delegate.serial_number

    @property
    def name(self) -> str:
        return self._delegate.name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._delegate.id)
            },
            via_device=(DOMAIN, self._hub_id),
            manufacturer=self._delegate.manufacturer,
            model=self._delegate.model,
            name=self._delegate.name,
            serial_number=self._delegate.serial_number,
            sw_version=self._delegate.firmware_version,
        )

    async def async_update(self) -> None:
        await self._delegate.update_state()


class IkeaDirigeraToggleEntity(IkeaDirigeraEntity):

    @property
    def is_on(self) -> bool:
        return self._delegate.is_on

    async def async_turn_on(self) -> None:
        await self._delegate.turn_on()

    async def async_turn_off(self) -> None:
        await self._delegate.turn_off()
