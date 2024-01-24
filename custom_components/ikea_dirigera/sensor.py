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
    def async_add_environment_sensor(device_id: str, device_info: DeviceInfo):
        temperature_sensor = IkeaDirigeraTemperatureSensorEntity(hub_api, device_id, device_info)
        humidity_sensor = IkeaDirigeraHumiditySensorEntity(hub_api, device_id, device_info)
        async_add_entities([temperature_sensor, humidity_sensor])

    device_details = await hub_api.get_devices()
    for device_detail in device_details:
        device_type = device_detail["deviceType"]
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

        if device_type == "environmentSensor":
            async_add_environment_sensor(device_id, device_info)


class IkeaDirigeraSensorEntity(IkeaDirigeraEntity, SensorEntity):
    entity_description = SensorEntityDescription(
        key="ikea_dirigera_sensor",
        has_entity_name=True,
        name=None
    )

    _api: DeviceAPI 

    def __init__(self, hub_api: HubAPI, id: str, sensor_device_class: SensorDeviceClass, device_info: DeviceInfo):
        super().__init__(f"{id}_{sensor_device_class}", device_info)
        self._attr_device_class = sensor_device_class
        self._api = DeviceAPI(hub_api, id)


class IkeaDirigeraTemperatureSensorEntity(IkeaDirigeraSensorEntity): 
    def __init__(self, hub_api: HubAPI, id: str, device_info: DeviceInfo):
        super().__init__(hub_api, id, SensorDeviceClass.TEMPERATURE, device_info)

    async def async_update(self) -> None:
        status = await self._api.get_status()
        self._attr_native_value = status["attributes"]["currentTemperature"]
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class IkeaDirigeraHumiditySensorEntity(IkeaDirigeraSensorEntity): 
    def __init__(self, hub_api: HubAPI, id: str, device_info: DeviceInfo):
        super().__init__(hub_api, id, SensorDeviceClass.HUMIDITY, device_info)

    async def async_update(self) -> None:
        status = await self._api.get_status()
        self._attr_native_value = status["attributes"]["currentRH"]
        self._attr_native_unit_of_measurement = PERCENTAGE
