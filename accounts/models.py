from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


class Role(models.Model):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    GUARDIAN = "guardian"
    STAFF = "staff"
    ACCOUNTANT = "accountant"
    LIBRARIAN = "librarian"
    RECEPTIONIST = "receptionist"
    DRIVER = "driver"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (TEACHER, "Teacher"),
        (STUDENT, "Student"),
        (PARENT, "Parent"),
        (GUARDIAN, "Guardian"),
        (STAFF, "Staff"),
        (ACCOUNTANT, "Accountant"),
        (LIBRARIAN, "Librarian"),
        (RECEPTIONIST, "Receptionist"),
        (DRIVER, "Driver"),
    ]

    name = models.CharField(max_length=30, choices=ROLE_CHOICES, unique=True)
    is_system_role = models.BooleanField(
        default=True, help_text="True for built-in roles; False for custom roles admins create."
    )

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """
    Keep this model THIN. Student/Teacher/Staff-specific fields (photo, DOB,
    admission number, etc.) belong in Phase 3 profile models, not here.
    """
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="users", null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    is_active_employee = models.BooleanField(
        default=True, help_text="Toggle for the 'Active/Inactive' status shown across list pages."
    )
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name() or self.username


class OTPVerification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_verifications"
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.email} - {'used' if self.is_used else 'active'}"

    def is_expired(self):
        expiry = int(getattr(settings, "OTP_EXPIRY_SECONDS", 300))
        return (timezone.now() - self.created_at).total_seconds() > expiry