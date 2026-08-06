import uuid
from django.db import models
from core.models import AcademicYear
from django.conf import settings


class SchoolClass(models.Model):
    """'Class I', 'Class II'... shown as 'Classes' in the sidebar."""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=50)          # "Class I"
    numeric_order = models.PositiveIntegerField(help_text="For sorting: I=1, II=2 ...")

    class Meta:
        unique_together = ("academic_year", "name")
        ordering = ["numeric_order"]

    def __str__(self):
        return self.name


class Section(models.Model):
    """'A', 'B', 'C' within a class."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="sections")
    section_id = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=10)
    no_of_students = models.PositiveIntegerField(default=0)
    no_of_subjects = models.PositiveIntegerField(default=0)
    room_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("school_class", "name")

    def __str__(self):
        return f"{self.school_class.name} - {self.name}"

    @property
    def display_id(self):
        return self.section_id if self.section_id else f"C{130000 + self.pk}"


class Subject(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="subjects")
    classes = models.ManyToManyField(SchoolClass, related_name="subjects", blank=True)
    subject_id = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    type = models.CharField(
        max_length=20,
        choices=[("theory", "Theory"), ("practical", "Practical")],
        default="theory",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def display_id(self):
        return self.subject_id if self.subject_id else f"SU{128400 + self.pk}"




class ClassRoom(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    room_id = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=50)              # "Room 101"
    room_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(default=30)
    floor = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def display_id(self):
        return self.room_id if self.room_id else f"R{167650 + self.pk}"


class Syllabus(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="syllabi")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="syllabi", null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="syllabi", null=True, blank=True)
    subject_group = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="syllabus/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} ({self.school_class} - {self.subject_group})"


DAY_CHOICES = [
    ("mon", "Monday"), ("tue", "Tuesday"), ("wed", "Wednesday"),
    ("thu", "Thursday"), ("fri", "Friday"), ("sat", "Saturday"),
]


class TimeTableEntry(models.Model):
    """Powers both 'Class Routine' and 'Time Table' pages — same data, different views."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="timetable_entries")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="timetable_entries")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetable_entries")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="timetable_entries"
    )
    routine_id = models.CharField(max_length=50, blank=True)
    room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.school_class}-{self.section} {self.subject} ({self.day})"

    @property
    def display_id(self):
        return self.routine_id if self.routine_id else f"RT{100000 + self.pk}"


class Schedule(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    schedule_id = models.CharField(max_length=20, unique=True, editable=False)
    schedule_type = models.CharField(max_length=50, default="Class")
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.schedule_id} ({self.start_time} - {self.end_time})"

    def save(self, *args, **kwargs):
        if not self.schedule_id:
            numbers = []
            for sid in Schedule.objects.values_list("schedule_id", flat=True):
                if sid and sid.startswith("S") and sid[1:].isdigit():
                    numbers.append(int(sid[1:]))
            candidate = max(numbers) + 1 if numbers else 148231
            while Schedule.objects.filter(schedule_id=f"S{candidate}").exists():
                candidate += 1
            self.schedule_id = f"S{candidate}"
        super().save(*args, **kwargs)


class HomeWork(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    homework_id = models.CharField(max_length=20, unique=True, editable=False)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="homeworks")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="homeworks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="homeworks")
    homework_date = models.DateField()
    submission_date = models.DateField()
    attachments = models.FileField(upload_to="homework/attachments/", blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="homeworks_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-homework_date", "-created_at"]

    def __str__(self):
        return f"{self.homework_id} - {self.school_class.name} {self.section.name} - {self.subject.name}"

    def save(self, *args, **kwargs):
        if not self.homework_id:
            numbers = []
            for hwid in HomeWork.objects.values_list("homework_id", flat=True):
                if hwid and hwid.startswith("HW") and hwid[2:].isdigit():
                    numbers.append(int(hwid[2:]))
            candidate = max(numbers) + 1 if numbers else 1000001
            while HomeWork.objects.filter(homework_id=f"HW{candidate}").exists():
                candidate += 1
            self.homework_id = f"HW{candidate}"
        super().save(*args, **kwargs)


class AcademicReason(models.Model):
    ROLE_CHOICES = [
        ("Teacher", "Teacher"),
        ("Student", "Student"),
        ("Staff", "Staff"),
    ]
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Teacher")
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Academic Reason"
        verbose_name_plural = "Academic Reasons"

    def __str__(self):
        return f"{self.role} - {self.reason}"



