from django.db import models
from academics.models import SchoolClass, Section
from people.models import Student


class ClassReport(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="class_reports")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="class_reports")
    report_date = models.DateField(auto_now_add=True)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("school_class", "section")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.school_class.name} - {self.section.name}"

    @property
    def display_id(self):
        return f"C{130000 + self.pk}"

    @property
    def no_of_students(self):
        return self.section.no_of_students

    @property
    def student_count(self):
        return self.section.students.count()


class StudentReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_reports")
    report_date = models.DateField(auto_now_add=True)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.name} ({self.student.admission_no})"

    @property
    def display_id(self):
        return f"S{130000 + self.pk}"

    @property
    def roll_no(self):
        return self.student.roll_no
