from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TaskNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')
        if self.user_id:
            self.group_name = f"user_{self.user_id}"
        else:
            self.group_name = "task_updates"
        
        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_task_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def notify(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
