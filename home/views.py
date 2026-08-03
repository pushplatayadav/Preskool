from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from academics.models import (
    SchoolClass, Section, Subject, TimeTableEntry, Schedule, HomeWork,
    Syllabus, ClassRoom,
)
from exam.models import Exam, ExamAttendance, ExamResult, Grade
from core.models import AcademicYear, School
from people.models import Student
from accounts.models import User


def home(request):
    now = timezone.now()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()
    school_name = school.name if school else "Global International"

    # ── Student counts ──
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status="active").count()
    inactive_students = Student.objects.filter(status="inactive").count()

    # ── Teacher counts (users whose role is "teacher") ──
    from accounts.models import Role
    teacher_role = Role.objects.filter(name=Role.TEACHER).first()
    total_teachers = User.objects.filter(role=teacher_role).count() if teacher_role else 0
    active_teachers = User.objects.filter(role=teacher_role, is_active_employee=True).count() if teacher_role else 0
    inactive_teachers = total_teachers - active_teachers

    # ── Staff counts (non-teacher employee roles) ──
    staff_roles = Role.objects.filter(
        name__in=[Role.STAFF, Role.ACCOUNTANT, Role.LIBRARIAN, Role.RECEPTIONIST, Role.DRIVER]
    )
    total_staff = User.objects.filter(role__in=staff_roles).count() if staff_roles else 0
    active_staff = User.objects.filter(role__in=staff_roles, is_active_employee=True).count() if staff_roles else 0
    inactive_staff = total_staff - active_staff

    # ── Subject counts ──
    total_subjects = Subject.objects.filter(academic_year=current_academic_year).count() if current_academic_year else Subject.objects.count()
    active_subjects = Subject.objects.filter(is_active=True).count()

    # ── Scheduled events (from Schedule model) ──
    schedules = Schedule.objects.filter(status="active")[:5]

    # ── Attendance stats (placeholder – real attendance not fully modelled yet) ──
    # We show the same numbers from the template but could expand later

    # ── Time-table / Class Routine ──
    timetable_entries = TimeTableEntry.objects.select_related(
        "school_class", "section", "subject", "teacher", "room"
    )[:5]

    # ── Exams / Results ──
    exams = Exam.objects.filter(status="active").select_related(
        "school_class", "section", "subject", "room"
    )[:5]

    # ── Class list for dropdowns ──
    classes = SchoolClass.objects.filter(
        academic_year=current_academic_year
    ).order_by("numeric_order") if current_academic_year else SchoolClass.objects.all()

    sections = Section.objects.select_related("school_class").all()

    # ── Active subjects list ──
    active_subjects_list = Subject.objects.filter(is_active=True, academic_year=current_academic_year) if current_academic_year else Subject.objects.filter(is_active=True)

    # ── Recent students for activity ──
    students = Student.objects.select_related("school_class", "section").order_by("-created_at")[:8]

    # ── Class-wise counts for student grid on dash ──
    class_student_counts = (
        Student.objects.values("school_class__name")
        .annotate(total=Count("id"), active=Count("id", filter=Q(status="active")))
        .order_by("school_class__numeric_order")
    )

    return render(request, "portaluser/home/index.html", {
        # School
        "school_name": school_name,
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),

        # Counts
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,

        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "inactive_teachers": inactive_teachers,

        "total_staff": total_staff,
        "active_staff": active_staff,
        "inactive_staff": inactive_staff,

        "total_subjects": total_subjects,
        "active_subjects": active_subjects,
        "inactive_subjects": total_subjects - active_subjects,

        # Lists
        "classes": classes,
        "sections": sections,
        "class_student_counts": class_student_counts,
        "schedules": schedules,
        "timetable_entries": timetable_entries,
        "exams": exams,

        # Placeholder counters for attendance (static values shown in design)
        "active_subjects_list": active_subjects_list,
        "students": students,
        "student_emergency": 28,
        "student_absent": 1,
        "student_late": 1,
        "teacher_emergency": 30,
        "teacher_absent": 3,
        "teacher_late": 3,
        "staff_emergency": 45,
        "staff_absent": 1,
        "staff_late": 10,
    })