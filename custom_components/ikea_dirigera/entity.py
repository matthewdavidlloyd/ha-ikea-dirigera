from typing import Optional

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class IkeaDirigeraEntity(Entity):

    _hub_id: str
    _device_id: str
    _device_name: str
    _device_manufacturer: Optional[str]
    _device_model: Optional[str]
    _device_serial_number: Optional[str]
    _device_software_version: Optional[str]

    def __init__(
        self,
        hub_id: str,
        device_id: str,
        device_name: str,
        device_manufacturer: str = None,
        device_model: str = None,
        device_serial_number: str = None,
        device_software_version: str = None  
    ):
        self._hub_id = hub_id
        self._device_id = device_id
        self._device_name = device_name
        self._device_manufacturer = device_manufacturer
        self._device_model = device_model
        self._device_serial_number = device_serial_number
        self._device_software_version = device_software_version

    @property
    def unique_id(self) -> str:
        return self._device_serial_number

    @property
    def name(self) -> str:
        return self._device_name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={
                (DOMAIN, self._device_id)
            },
            via_device=(DOMAIN, self._hub_id),
            manufacturer=self._device_manufacturer,
            model=self._device_model,
            name=self._device_name,
            serial_number=self._device_serial_number,
            sw_version=self._device_software_version,
        )
