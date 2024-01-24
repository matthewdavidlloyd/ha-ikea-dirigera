from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity


class IkeaDirigeraEntity(Entity):
    def __init__(self, id: str, device_info: DeviceInfo):
        self._attr_unique_id = id
        self._attr_device_info = device_info
