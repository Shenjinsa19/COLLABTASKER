from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
User = get_user_model()

class ActivityLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE,null=True, blank=True, related_name="activity_logs")
    user=models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    action=models.CharField(max_length=255)
    timestamp=models.DateTimeField(auto_now_add=True)
    metadata=models.JSONField(blank=True, null=True)  
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"
