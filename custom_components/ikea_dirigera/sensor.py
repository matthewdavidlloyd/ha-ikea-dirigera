from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import callback, HomeAssistant
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import ranged_value_to_percentage, percentage_to_ranged_value

from .vendor.pydirigera.device import DeviceAPI
from .vendor.pydirigera.hub import HubAPI

from .const import DOMAIN, CONF_HUB_ID
from .entity import IkeaDirigeraEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    hub_id: str = entry.data[CONF_HUB_ID]
    hub_api: HubAPI = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_environment_sensor(device_id: str, device_name: str, **kwargs):
        temperature_sensor = IkeaDirigeraTemperatureSensorEntity(hub_api, hub_id, device_id, device_name, **kwargs)
        humidity_sensor = IkeaDirigeraHumiditySensorEntity(hub_api, hub_id, device_id, device_name, **kwargs)
        async_add_entities([temperature_sensor, humidity_sensor])

    device_details = await hub_api.get_devices()
    for device_detail in device_details:
        device_type = device_detail["deviceType"]
        device_id = device_detail["id"]
        device_name = device_detail["attributes"]["customName"]

        if device_type == "environmentSensor":
            async_add_environment_sensor(
                device_id,
                device_name,
                device_manufacturer = device_detail["attributes"]["manufacturer"],
                device_model = device_detail["attributes"]["model"],
                device_serial_number = device_detail["attributes"]["serialNumber"],
                device_software_version = device_detail["attributes"]["firmwareVersion"] 
            )


class IkeaDirigeraSensorEntity(IkeaDirigeraEntity, SensorEntity):

    _api: DeviceAPI 

    def __init__(
            self,
            hub_api: HubAPI,
            hub_id: str,
            device_id: str,
            device_name: str,
            device_manufacturer: str = None,
            device_model: str = None,
            device_serial_number: str = None,
            device_software_version: str = None  
        ):
            super().__init__(hub_id, device_id, device_name, device_manufacturer, device_model, device_serial_number, device_software_version)
            self._api = DeviceAPI(hub_api, device_id)

    @property
    def unique_id(self) -> str:
        return f"{self._device_serial_number}-{self._attr_device_class}"

    @property
    def name(self) -> str:
        return f"""{self._device_name} {self._attr_device_class.replace("_", " ")}"""

    @property
    def entity_description(self) -> SensorEntity:
        return SensorEntityDescription(key="ikea_dirigera_sensor", has_entity_name=True, name=None)


class IkeaDirigeraTemperatureSensorEntity(IkeaDirigeraSensorEntity):
    
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        
    async def async_update(self) -> None:
        status = await self._api.get_status()
        self._attr_native_value = status["attributes"]["currentTemperature"]


class IkeaDirigeraHumiditySensorEntity(IkeaDirigeraSensorEntity):
    
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    async def async_update(self) -> None:
        status = await self._api.get_status()
        self._attr_native_value = status["attributes"]["currentRH"]
