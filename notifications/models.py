from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}"
