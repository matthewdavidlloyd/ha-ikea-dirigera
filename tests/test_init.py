from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.ikea_dirigera.const import DOMAIN
from custom_components.ikea_dirigera.vendor.pydirigera.hub import HubAPI

from unittest.mock import MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .util import random_uuid, random_ip, random_string

async def test_async_setup_with_no_config(hass: HomeAssistant) -> None:
    result = await async_setup_component(hass, DOMAIN, {})
    
    assert result is True
    assert hass.config_entries.async_entries() == []

@patch.object(
        HubAPI,
        "get_hub_status",
        return_value={
            "attributes": {
                "customName": "Home",
                "model": "DIRIGERA Hub for smart products",
                "manufacturer": "IKEA of Sweden",
                "firmwareVersion": "2.391.4",
            }
        }
)
async def test_async_setup(mock_get_hub_status: MagicMock, hass: HomeAssistant) -> None:
    # Setup
    
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "hub_id": random_uuid(),
            "ip_address": random_ip(),
            "token": random_string(128)
        }
    )
    entry.add_to_hass(hass)

    # Do

    result = await async_setup_component(hass, DOMAIN, {})

    # Assert

    assert result is True

    assert hass.config_entries.async_entries() == [entry]
    
    # TODO: Better device registration assertions
    # device_registry = hass.data["device_registry"]
    # devices = device_registry.devices.data
    # assert len(devices) == 1
