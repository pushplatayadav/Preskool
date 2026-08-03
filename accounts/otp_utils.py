import random
import string

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from .models import OTPVerification


def generate_otp(user):
    length = int(getattr(settings, "OTP_LENGTH", 6))
    otp_code = "".join(random.choices(string.digits, k=length))

    OTPVerification.objects.filter(user=user, is_used=False).update(is_used=True)

    OTPVerification.objects.create(user=user, otp_code=otp_code)

    expiry_seconds = int(getattr(settings, "OTP_EXPIRY_SECONDS", 300))
    expiry_minutes = expiry_seconds // 60

    html_message = render_to_string("emails/otp_email.html", {
        "user": user,
        "otp_code": otp_code,
        "expiry_minutes": expiry_minutes,
    })

    mail = EmailMessage(
        subject="Preskool - Email Verification OTP",
        body=html_message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
        to=[user.email],
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)

    return otp_code


def verify_otp(user, code):
    try:
        otp = OTPVerification.objects.filter(
            user=user, otp_code=code, is_used=False
        ).latest("created_at")
    except OTPVerification.DoesNotExist:
        return False, "Invalid OTP code."

    if otp.is_expired():
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return False, "OTP has expired. Please request a new one."

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    user.is_email_verified = True
    user.save(update_fields=["is_email_verified"])

    return True, "Email verified successfully!"


def generate_password_reset_otp(user):
    length = int(getattr(settings, "OTP_LENGTH", 6))
    otp_code = "".join(random.choices(string.digits, k=length))

    OTPVerification.objects.filter(user=user, is_used=False).update(is_used=True)

    OTPVerification.objects.create(user=user, otp_code=otp_code)

    expiry_seconds = int(getattr(settings, "OTP_EXPIRY_SECONDS", 300))
    expiry_minutes = expiry_seconds // 60

    html_message = render_to_string("emails/password_reset_otp_email.html", {
        "user": user,
        "otp_code": otp_code,
        "expiry_minutes": expiry_minutes,
    })

    mail = EmailMessage(
        subject="Preskool - Password Reset OTP",
        body=html_message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
        to=[user.email],
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)

    return otp_code


def verify_password_reset_otp(user, code):
    try:
        otp = OTPVerification.objects.filter(
            user=user, otp_code=code, is_used=False
        ).latest("created_at")
    except OTPVerification.DoesNotExist:
        return False, "Invalid OTP code."

    if otp.is_expired():
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return False, "OTP has expired. Please request a new one."

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    if not user.is_email_verified:
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

    return True, "OTP verified successfully!"
