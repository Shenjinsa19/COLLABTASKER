from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from projects.models import Project, Task
from logs.models import ActivityLog
from .models import Notification  


#  creation activity
@receiver(post_save, sender=Project)
def log_project_created(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            project=instance,
            action=f"Project '{instance.name}' created by {instance.created_by.email}"
        )

@receiver(m2m_changed, sender=Project.members.through)
def notify_members_on_assignment(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            ActivityLog.objects.create(
                project=instance,
                action=f"User with ID {user_id} assigned to project '{instance.name}'"
            )
        # user = CustomUser.objects.get(pk=user_id)

def send_realtime_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "notify", 
            "message": message,
        }
    )


# notify  instance on task create/update
@receiver(post_save, sender=Task)
def notify_task_assignment(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        message = f"You have been assigned a new task: '{instance.title}'"
        Notification.objects.create(user=instance.assigned_to, message=message)
        send_realtime_notification(instance.assigned_to.id, message)

    elif instance.status == 'Completed':
        message = f"Task '{instance.title}' completed by {instance.assigned_to.email}"
        Notification.objects.create(user=instance.created_by, message=message)
        send_realtime_notification(instance.created_by.id, message)

    channel_layer = get_channel_layer()
    message_payload = {
        "event": "Task Created" if created else "Task Updated",
        "task": {
            "id": instance.id,
            "title": instance.title,
            "project": instance.project.name,
            "assigned_to": instance.assigned_to.email if instance.assigned_to else None,
            "status": instance.status,
            "priority": instance.priority,
        }
    }
    async_to_sync(channel_layer.group_send)(
        "task_updates",
        {
            "type": "send_task_notification",
            "message": message_payload,
        }
    )
