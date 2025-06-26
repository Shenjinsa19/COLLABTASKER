from celery import shared_task
from django.core.mail import send_mail
@shared_task
def send_welcome_email(email, subject, message):
    try:
        print(f"Sending welcome email to {email}")
        send_mail(
            subject,
            message,
            'spmacavity@gmail.com',
            [email],
            fail_silently=False,  # Important: this raises errors
        )
        print("Email sent successfully.")
    except Exception as e:
        print(" Error sending email:", str(e))

