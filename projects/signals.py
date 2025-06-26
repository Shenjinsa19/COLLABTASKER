from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Project

@receiver(m2m_changed, sender=Project.members.through)
def notify_members_on_assignment(sender, instance, action, pk_set, **kwargs):
    if action=="post_add":  # After members are added
        members=instance.members.filter(pk__in=pk_set)
        for member in members:
            send_mail(
                subject=f"You have been added to project: {instance.name}",
                message=f"Hello {member.get_full_name() or member.username},\n\n"
                        f"You have been assigned to the project '{instance.name}'. Please check your dashboard.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member.email],
                fail_silently=False,
            )
