
from django.db import models
from django.conf import settings
from projects.models import Project

class ChatMessage(models.Model):
    project=models.ForeignKey(Project, on_delete=models.CASCADE,related_name='chat_messages')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.CASCADE)
    message=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.project.name} - {self.timestamp}'

