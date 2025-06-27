from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import Task,Project


# @shared_task
# def send_task_assignment_email(user_email, task_title):
#     subject=f'New Task Assigned: {task_title}'
#     message=f'You have been assigned a new task : {task_title}'
#     # message = f'You have been assigned a new task in project: {project_name}\nTask: {task_title}'
#     from_email='spmacavity@gmail.com'  
#     sent = send_mail(subject, message, from_email, [user_email])
#     if sent:
#         print(f" Email successfully sent to {user_email} for task '{task_title}'")
#     else:
#         print(f"Failed to send email to {user_email} for task '{task_title}'")

@shared_task
def send_task_assignment_email(user_email, task_title):
    try:
        # Get the task by title (assuming title is unique, otherwise this may return multiple tasks)
        task = Task.objects.get(title=task_title)
    except Task.DoesNotExist:
        print(f"Task with title '{task_title}' does not exist.")
        return

    subject = f'New Task Assigned: {task.title}'
    message = (
        f'Hello,\n\n'
        f'You have been assigned a new task in the project "{task.project.name}".\n\n'
        f'Task Details:\n'
        f'Title: {task.title}\n'
        f'Description: {task.description or "No description provided"}\n'
        f'Deadline: {task.deadline.strftime("%B %d, %Y")}\n'
        f'Priority: {task.get_priority_display()}\n'
        f'Status: {task.get_status_display()}\n\n'
        f'Please make sure to complete it on time.\n\n'
        f'Best regards,\n'
        f'CollabTasker Team'
    )
    from_email = 'spmacavity@gmail.com'
    sent = send_mail(subject, message, from_email, [user_email])
    if sent:
        print(f"Email successfully sent to {user_email} for task '{task.title}'")
    else:
        print(f"Failed to send email to {user_email} for task '{task.title}'")

@shared_task
def send_task_deadline_reminders():
    upcoming_deadline = datetime.now() + timedelta(minutes=60)
    tasks = Task.objects.filter(deadline__lte=upcoming_deadline, status__in=['todo', 'inrogress'])
    if not tasks:
        print("No tasks due soon; no emails sent.")
        return
    for task in tasks:
        user_email = task.assigned_to.email if task.assigned_to else None
        if user_email:
            subject = f"Reminder: Task '{task.title}' deadline is near"
            message = f"Your task '{task.title}' is due soon. Please make sure to complete it."
            from_email = 'spmacavity@gmail.com'
            sent = send_mail(subject, message, from_email, [user_email])
            if sent:
                print(f"Reminder email sent to {user_email} for task '{task.title}'")
            else:
                print(f"Failed to send reminder to {user_email} for task '{task.title}'")





