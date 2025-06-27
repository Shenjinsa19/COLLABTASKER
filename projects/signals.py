from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Project

@receiver(m2m_changed, sender=Project.members.through)
def notify_members_on_assignment(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        members = instance.members.filter(pk__in=pk_set)
        for member in members:
            subject = f"You've been added to the project: {instance.name}"
            message = f"""
Hi {member.name},

You have been added to a new project on CollabTasker.

📌 Project Name: {instance.name}
📝 Description: {instance.description or "No description provided"}
👤 Assigned By: {instance.created_by.name}
📅 Assigned On: {instance.created_at.strftime('%B %d, %Y at %I:%M %p')}

Thanks for being part of the team!

— CollabTasker Team
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.email],
                fail_silently=False,
            )
