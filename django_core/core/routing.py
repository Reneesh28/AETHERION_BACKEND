from django.urls import re_path
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LiveConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "live_updates"

    async def connect(self):
        user = self.scope.get("user")

        if user is None or user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "message": "WebSocket authenticated and connected."
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def live_message(self, event):
        """
        Handler for broadcast messages sent to group.
        """
        await self.send(text_data=json.dumps({
            "channel": event.get("channel"),
            "data": event.get("data")
        }))


websocket_urlpatterns = [
    re_path(r"^ws/live/$", LiveConsumer.as_asgi()),
]