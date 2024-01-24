from .hub import HubAPI


class DeviceAPI:
    _hub_api: HubAPI
    _id: str

    def __init__(self, hub: HubAPI, id: str):
        self._id = id
        self._hub_api = hub

    async def get_status(self):
        return await self._hub_api.get_device_status(self._id)


class OnOffDeviceAPI(DeviceAPI):
    async def turn_on(self) -> None:
        await self._hub_api.update_device_status(
            self._id,
            [{"attributes": {"isOn": True}}]
        )

    async def turn_off(self) -> None:
        await self._hub_api.update_device_status(
            self._id,
            [{"attributes": {"isOn": False}}]
        )


class LightAPI(OnOffDeviceAPI):
    async def set_light_level(self, light_level: int) -> None:
        if light_level < 1 or light_level > 100:
            raise ValueError("Light level must be in range [1, 100]")
        
        await self._hub_api.update_device_status(
            self._id,
            [{"attributes": {"lightLevel": light_level}}]
        )
