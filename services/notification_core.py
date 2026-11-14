
import asyncio
import httpx
from abc import ABC, abstractmethod


class NotificationChannel(ABC):

    @abstractmethod
    async def send(self, destination: str, message: str) -> None:
        pass


class EmailNotification(NotificationChannel):

    async def send(self, destination: str, message: str) -> None:
        print(f"SMTP: Enviando a {destination}")
        await asyncio.sleep(0.1)


class SMSNotification(NotificationChannel):

    async def send(self, destination: str, message: str) -> None:
        print(f"Twilio API: Enviando SMS a {destination}")
        await asyncio.sleep(0.2)


class WebhookNotification(NotificationChannel):

    async def send(self, destination: str, message: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                destination,
                json={"message": message},
                timeout=5.0
            )


class NotificationDispatcher:

    def __init__(self, channels: dict[str, NotificationChannel] = None):
        self.channels = channels or {
            "email": EmailNotification(),
            "sms": SMSNotification(),
            "webhook": WebhookNotification()
        }

    async def send_alerts(
        self,
        channels: list[str],
        destination: str,
        message: str
    ) -> None:
        tasks = []

        for channel in channels:
            notifier = self.channels.get(channel)

            if notifier is None:
                raise ValueError(
                    f"Canal no soportado: {channel}"
                )

            tasks.append(
                notifier.send(destination, message)
            )

        await asyncio.gather(*tasks)
