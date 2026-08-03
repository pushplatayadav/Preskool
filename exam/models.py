import uuid
from django.db import models
from academics.models import SchoolClass, Section, Subject, ClassRoom
from django.conf import settings


class Exam(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    exam_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exams")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="exams")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exams")
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.PositiveIntegerField(default=100)
    pass_marks = models.PositiveIntegerField(default=33)
    room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="exams")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="exams_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "academics"
        ordering = ["-exam_date", "-created_at"]

    def __str__(self):
        return f"{self.exam_id} - {self.name} ({self.school_class.name} {self.section.name})"

    def save(self, *args, **kwargs):
        if not self.exam_id:
            self.exam_id = f"EXM{uuid.uuid4().int % 10000000:07d}"
        super().save(*args, **kwargs)

    @property
    def display_id(self):
        return self.exam_id


class Grade(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    grade_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=20)
    min_marks = models.PositiveIntegerField()
    max_marks = models.PositiveIntegerField()
    grade_point = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "academics"
        ordering = ["-min_marks"]

    def __str__(self):
        return f"{self.name} ({self.min_marks}-{self.max_marks})"

    def save(self, *args, **kwargs):
        if not self.grade_id:
            self.grade_id = f"GR{uuid.uuid4().int % 1000000:07d}"
        super().save(*args, **kwargs)

    @property
    def display_id(self):
        return self.grade_id


class ExamSchedule(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    schedule_id = models.CharField(max_length=20, unique=True, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="schedules")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exam_schedules")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="exam_schedules")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exam_schedules")
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="exam_schedules")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "academics"
        ordering = ["-exam_date", "start_time"]

    def __str__(self):
        return f"{self.schedule_id} - {self.exam.name} ({self.subject.name})"

    def save(self, *args, **kwargs):
        if not self.schedule_id:
            self.schedule_id = f"ES{uuid.uuid4().int % 10000000:07d}"
        super().save(*args, **kwargs)

    @property
    def display_id(self):
        return self.schedule_id


class ExamAttendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]

    student = models.ForeignKey("people.Student", on_delete=models.CASCADE, related_name="exam_attendances")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="present")
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "academics"
        unique_together = ("student", "exam")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.name} - {self.exam.name} ({self.get_status_display()})"


class ExamResult(models.Model):
    student = models.ForeignKey("people.Student", on_delete=models.CASCADE, related_name="exam_results")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="exam_results")
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "academics"
        unique_together = ("student", "exam")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.marks_obtained}"

    @property
    def percentage(self):
        if self.exam and self.exam.total_marks > 0:
            return round((float(self.marks_obtained) / self.exam.total_marks) * 100, 1)
        return 0

    @property
    def is_passed(self):
        if self.exam:
            return float(self.marks_obtained) >= self.exam.pass_marks
        return False
