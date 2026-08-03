from django.contrib import admin
from .models import Student, StudentLeave, StudentAttendance, Teacher, Staff, TeacherAttendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("admission_no", "name", "school_class", "section", "gender", "parent_name", "status")
    list_filter = ("school_class", "section", "gender", "status")
    search_fields = ("admission_no", "name", "parent_name")


@admin.register(StudentLeave)
class StudentLeaveAdmin(admin.ModelAdmin):
    list_display = ("student", "leave_type", "from_date", "to_date", "no_of_days", "status", "applied_on")
    list_filter = ("leave_type", "status")
    search_fields = ("student__name", "student__admission_no")


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status")
    list_filter = ("status", "date")
    search_fields = ("student__name", "student__admission_no")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("teacher_id", "name", "school_class", "subject", "email", "phone", "status")
    list_filter = ("school_class", "subject", "status", "gender")
    search_fields = ("teacher_id", "name", "email", "phone")


@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ("teacher", "date", "status")
    list_filter = ("status", "date")
    search_fields = ("teacher__name", "teacher__teacher_id")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("staff_id", "name", "department", "designation", "email", "phone", "status")
    list_filter = ("department", "designation", "status", "gender")
    search_fields = ("staff_id", "name", "email", "phone", "department", "designation")
