from django.conf import settings
from django.db import models

from accounts.models import Role


class Event(models.Model):
    """Event / activity published on the school events calendar."""

    EVENT_FOR_CHOICES = [
        ("all", "All"),
        ("students", "Students"),
        ("staffs", "Staffs"),
    ]
    CATEGORY_CHOICES = [
        ("celebration", "Celebration"),
        ("training", "Training"),
        ("meeting", "Meeting"),
        ("holidays", "Holidays"),
        ("camp", "Camp"),
    ]

    title = models.CharField(max_length=200)
    event_for = models.CharField(max_length=20, choices=EVENT_FOR_CHOICES, default="all")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="meeting")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    attachment = models.FileField(upload_to="events/", blank=True, null=True)
    message = models.TextField(blank=True)
    classes = models.ManyToManyField(
        "academics.SchoolClass", related_name="events", blank=True
    )
    sections = models.ManyToManyField(
        "academics.Section", related_name="events", blank=True
    )
    roles = models.ManyToManyField(
        "accounts.Role", related_name="events", blank=True
    )
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="events", blank=True
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]

    def __str__(self):
        return self.title

    def category_display(self):
        return self.get_category_display()

    def event_for_display(self):
        return self.get_event_for_display()

    def classes_display(self):
        names = [c.name for c in self.classes.all()]
        return ", ".join(names) if names else "All Classes"

    def sections_display(self):
        names = [s.name for s in self.sections.all()]
        return ", ".join(names) if names else "All Sections"

    def roles_display(self):
        names = [r.get_name_display() for r in self.roles.all()]
        return ", ".join(names) if names else "-"

    def teachers_names(self):
        names = []
        for teacher in self.teachers.all():
            names.append(teacher.get_full_name() or teacher.username)
        return names

    def attachment_name(self):
        if not self.attachment:
            return ""
        return self.attachment.name.rsplit("/", 1)[-1]

    def added_by_name(self):
        user = self.added_by
        if not user:
            return "-"
        return user.get_full_name() or user.username


class NoticeBoard(models.Model):
    """Notice / announcement published on the school notice board."""

    title = models.CharField(max_length=200)
    notice_date = models.DateField()
    publish_on = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to="notice_board/", blank=True, null=True)
    message = models.TextField(blank=True)
    message_to = models.ManyToManyField(
        Role, related_name="notices", blank=True, help_text="Roles this notice is published to."
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notices",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-notice_date", "-created_at"]

    def __str__(self):
        return self.title

    def message_to_names(self):
        names = [role.get_name_display() for role in self.message_to.all()]
        return ", ".join(names) if names else "-"

    def attachment_name(self):
        if not self.attachment:
            return ""
        return self.attachment.name.rsplit("/", 1)[-1]

    def added_by_name(self):
        user = self.added_by
        if not user:
            return "-"
        return user.get_full_name() or user.username
