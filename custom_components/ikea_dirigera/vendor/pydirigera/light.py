from .hub import Hub

class Light:

    _id: str

    _hub: Hub

    def __init__(self, id: str, hub: Hub):
        self._id = id
        self._hub = hub

    async def get_status(self):
        return await self._hub.get_device_status(self._id)

    async def turn_on(self) -> None:
        await self._hub.update_device_status(
            self._id,
            [{"attributes": {"isOn": True}}]
        )

    async def turn_off(self) -> None:
        await self._hub.update_device_status(
            self._id,
            [{"attributes": {"isOn": False}}]
        )

    async def set_light_level(self, light_level: int) -> None:
        if light_level < 1 or light_level > 100:
            raise ValueError("Light level must be in range [1, 100]")
        
        await self._hub.update_device_status(
            self._id,
            [{"attributes": {"lightLevel": light_level}}]
        )
