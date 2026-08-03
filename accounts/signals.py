from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

User = get_user_model()


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if instance.is_email_verified and not created:
        if not hasattr(instance, "_welcome_email_sent"):
            instance._welcome_email_sent = True
            subject = "Welcome to Preskool!"
            html_message = render_to_string("emails/welcome.html", {
                "user": instance,
            })

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[instance.email],
            )
            email.content_subtype = "html"
            email.send(fail_silently=True)
