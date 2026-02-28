from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class BroadcastService:

    GROUP_NAME = "live_updates"

    @staticmethod
    def send(channel: str, data: dict):
        """
        Broadcast message to all connected WebSocket clients.
        """

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            BroadcastService.GROUP_NAME,
            {
                "type": "live_message",
                "channel": channel,
                "data": data
            }
        )