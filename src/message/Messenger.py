from typing import Any, Awaitable, Callable


class AppMsg:
    def __init__(self, name: str, data: Any | None = None):
        self.name = name
        self.data = data
        self.result = None  # How to use this?

    @classmethod
    def make(cls, name: str, data: Any | None = None) -> "AppMsg":
        return cls(name, data)


class Messenger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Messenger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "channels"):
            self.channels = dict()

    async def broadcast(self, channel: str, message: AppMsg):
        if channel in self.channels.keys():
            if message.name in self.channels[channel]:
                for handler in self.channels[channel][message.name]:
                    await handler(message)

    async def send(self, channel: str, message: str, data: Any | None = None):
        await self.broadcast(channel, AppMsg.make(message, data))

    def subscribe(
        self, channel: str, name: str, handler: Callable[[AppMsg], Awaitable[None]]
    ) -> None:
        if channel not in self.channels:
            self.channels[channel] = {name: [handler]}
        elif name not in self.channels[channel]:
            self.channels[channel][name] = [handler]
        else:
            self.channels[channel][name].append(handler)
