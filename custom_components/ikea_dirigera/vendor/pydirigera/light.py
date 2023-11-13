from .hub import Hub

class Light:

    _id: str

    _hub: Hub

    def __init__(self, id: str, hub: Hub):
        self._id = id
        self._hub = hub

    async def get_status(self):
        return await self._hub.get_device_status(self._id)

    async def set_light(self, lamp_on: bool) -> None:
        await self._hub.update_device_status(
            self._id,
            [{"attributes": {"isOn": lamp_on}}]
        )
