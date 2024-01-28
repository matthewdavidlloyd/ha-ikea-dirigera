from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import callback, HomeAssistant
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from aiodirigera.device import EnvironmentSensor
from aiodirigera.hub import Hub

from .const import DOMAIN, CONF_HUB_ID
from .entity import IkeaDirigeraEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    hub_id: str = entry.data[CONF_HUB_ID]
    hub: Hub = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_environment_sensor(environment_sensor: EnvironmentSensor):
        temperature_sensor = IkeaDirigeraTemperatureSensorEntity(
            hub_id,
            hub,
            environment_sensor
        )
        humidity_sensor = IkeaDirigeraHumiditySensorEntity(
            hub_id,
            hub,
            environment_sensor
        )
        async_add_entities([temperature_sensor, humidity_sensor])

    devices = await hub.get_devices()
    [
        async_add_environment_sensor(hub, device)
        for device in devices
        if type(device) is EnvironmentSensor
    ]


class IkeaDirigeraSensorEntity(IkeaDirigeraEntity, SensorEntity):
    entity_description = SensorEntityDescription(
        key="ikea_dirigera_sensor",
        has_entity_name=True,
        name=None
    )


class IkeaDirigeraTemperatureSensorEntity(IkeaDirigeraSensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> float:
        return self._delegate.temperature


class IkeaDirigeraHumiditySensorEntity(IkeaDirigeraSensorEntity):
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> float:
        return self._delegate.humidity
