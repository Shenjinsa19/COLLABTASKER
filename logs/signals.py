from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Project, Task
from .models import ActivityLog
from projects.tasks import send_task_assignment_email

# Mock notification function (replace with real implementation if needed)
def send_notification(user, message):
    print(f"Notification for {user.email}: {message}")

# Signal for logging project creation
@receiver(post_save, sender=Project)
def log_project_created(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.created_by,
            action=f"Created project '{instance.name}'",
            metadata={'project_id': instance.id}
        )

# Signal for logging task creation/update AND sending notification/email
@receiver(post_save, sender=Task)
def handle_task_creation_and_logging(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.created_by,
            action=f"Created task '{instance.title}' in project '{instance.project.name}'",
            metadata={'task_id': instance.id}
        )
    else:
        ActivityLog.objects.create(
            user=instance.updated_by,
            action=f"Updated task '{instance.title}'",
            metadata={'task_id': instance.id}
        )

    # Send notification and email if task assigned if neeeded/./.'lnb
    if instance.assigned_to and created:
        send_notification(instance.assigned_to, f"You were assigned to task '{instance.title}'")
        # send_task_assignment_email.delay(instance.assigned_to.email, instance.title)
