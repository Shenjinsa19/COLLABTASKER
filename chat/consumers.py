import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class ProjectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'chat_{self.project_id}'

        project_exists = await self.project_exists(self.project_id)
        if not project_exists:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()

        if not message:
            return

        user = self.scope.get("user", None)
        user_id = user.id if user and user.is_authenticated else None
        user_email = user.email if user and user.is_authenticated else "Anonymous"

        await self.save_message(self.project_id, user_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': user_email,
                'message': message,
            }
        )

    async def chat_message(self, event):
        user = event.get('user', 'Anonymous')
        message = event.get('message', '')
        logger.info(f"Sending message: user={user} message={message}")
        await self.send(text_data=json.dumps({
            'user': user,
            'message': message,
        }))

    @database_sync_to_async
    def save_message(self, project_id, user_id, message):
        from .models import ChatMessage
        from projects.models import Project
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None

        return ChatMessage.objects.create(project=project, user=user, message=message)

    @database_sync_to_async
    def project_exists(self, project_id):
        from projects.models import Project
        return Project.objects.filter(id=project_id).exists()
