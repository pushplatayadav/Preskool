import csv
import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Exam, Grade, ExamSchedule, ExamAttendance, ExamResult
from people.models import Student
from .forms import ExamForm, GradeForm, ExamScheduleForm, ExamAttendanceForm, ExamResultForm
from academics.models import SchoolClass, Section, Subject, ClassRoom
from core.models import AcademicYear, School


def _generate_exam_id():
    numbers = []
    for eid in Exam.objects.values_list("exam_id", flat=True):
        if eid and eid.startswith("EXM") and eid[3:].isdigit():
            numbers.append(int(eid[3:]))
    candidate = max(numbers) + 1 if numbers else 1000001
    while Exam.objects.filter(exam_id=f"EXM{candidate}").exists():
        candidate += 1
    return f"EXM{candidate}"


def _generate_grade_id():
    numbers = []
    for gid in Grade.objects.values_list("grade_id", flat=True):
        if gid and gid.startswith("GR") and gid[2:].isdigit():
            numbers.append(int(gid[2:]))
    candidate = max(numbers) + 1 if numbers else 1000001
    while Grade.objects.filter(grade_id=f"GR{candidate}").exists():
        candidate += 1
    return f"GR{candidate}"


def _generate_exam_schedule_id():
    numbers = []
    for esid in ExamSchedule.objects.values_list("schedule_id", flat=True):
        if esid and esid.startswith("ES") and esid[2:].isdigit():
            numbers.append(int(esid[2:]))
    candidate = max(numbers) + 1 if numbers else 1000001
    while ExamSchedule.objects.filter(schedule_id=f"ES{candidate}").exists():
        candidate += 1
    return f"ES{candidate}"


def exam_list(request):
    if request.method == "POST":
        if "add_exam" in request.POST:
            form = ExamForm(request.POST)
            if form.is_valid():
                exam = form.save(commit=False)
                posted_id = request.POST.get("exam_id", "").strip()
                if posted_id:
                    exam.exam_id = posted_id
                exam.created_by = request.user if request.user.is_authenticated else None
                exam.save()
                messages.success(request, "Exam added successfully.")
            else:
                messages.error(request, "Could not add exam. Please check the form.")
            return redirect("exam:exam-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Exam.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} exam(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("exam:exam-list")

    exams = Exam.objects.select_related("school_class", "section", "subject", "room").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_subject = request.GET.get("filter_subject", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_class:
        exams = exams.filter(school_class__name=filter_class)
    if filter_section:
        exams = exams.filter(section__name=filter_section)
    if filter_subject:
        exams = exams.filter(subject__name=filter_subject)
    if filter_status == "active":
        exams = exams.filter(status="active")
    elif filter_status == "inactive":
        exams = exams.filter(status="inactive")

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        exams = exams.order_by("-exam_date", "-name")
    else:
        exams = exams.order_by("exam_date", "name")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    subject_names = Subject.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    school_classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.all().order_by("school_class__numeric_order", "name")
    subjects = Subject.objects.all().order_by("name")
    classrooms = ClassRoom.objects.filter(status="active").order_by("room_number")

    return render(request, "portaluser/exam/exam.html", {
        "exams": exams,
        "class_names": class_names,
        "section_names": section_names,
        "subject_names": subject_names,
        "school_classes": school_classes,
        "sections": sections,
        "subjects": subjects,
        "classrooms": classrooms,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_exam_id": _generate_exam_id(),
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_subject": filter_subject,
        "filter_status": filter_status,
    })


def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            ex = form.save(commit=False)
            posted_id = request.POST.get("exam_id", "").strip()
            if posted_id:
                ex.exam_id = posted_id
            ex.save()
            messages.success(request, "Exam updated successfully.")
        else:
            messages.error(request, "Could not update exam.")
    return redirect("exam:exam-list")


def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        exam.delete()
        messages.success(request, "Exam deleted successfully.")
    return redirect("exam:exam-list")


def grade_list(request):
    if request.method == "POST":
        if "add_grade" in request.POST:
            form = GradeForm(request.POST)
            if form.is_valid():
                grade = form.save(commit=False)
                posted_id = request.POST.get("grade_id", "").strip()
                if posted_id:
                    grade.grade_id = posted_id
                grade.save()
                messages.success(request, "Grade added successfully.")
            else:
                messages.error(request, "Could not add grade. Please check the form.")
            return redirect("exam:grade-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Grade.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} grade(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("exam:grade-list")

    grades = Grade.objects.all()

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        grades = grades.order_by("-min_marks")
    else:
        grades = grades.order_by("min_marks")

    filter_grade = request.GET.get("filter_grade", "").strip()
    filter_percentage = request.GET.get("filter_percentage", "").strip()

    if filter_grade:
        grades = grades.filter(name=filter_grade)
    if filter_percentage:
        if filter_percentage == "90-100":
            grades = grades.filter(min_marks__gte=90, max_marks__lte=100)
        elif filter_percentage == "80-90":
            grades = grades.filter(min_marks__gte=80, max_marks__lte=90)
        elif filter_percentage == "70-80":
            grades = grades.filter(min_marks__gte=70, max_marks__lte=80)
        elif filter_percentage == "60-70":
            grades = grades.filter(min_marks__gte=60, max_marks__lte=70)
        elif filter_percentage == "50-60":
            grades = grades.filter(min_marks__gte=50, max_marks__lte=60)
        elif filter_percentage == "40-50":
            grades = grades.filter(min_marks__gte=40, max_marks__lte=50)
        elif filter_percentage == "35-40":
            grades = grades.filter(min_marks__gte=35, max_marks__lte=40)
        elif filter_percentage == "below-35":
            grades = grades.filter(max_marks__lt=35)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/exam/grade.html", {
        "grades": grades,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_grade_id": _generate_grade_id(),
        "sort": sort,
        "filter_grade": filter_grade,
        "filter_percentage": filter_percentage,
    })


def grade_edit(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            gr = form.save(commit=False)
            posted_id = request.POST.get("grade_id", "").strip()
            if posted_id:
                gr.grade_id = posted_id
            gr.save()
            messages.success(request, "Grade updated successfully.")
        else:
            messages.error(request, "Could not update grade.")
    return redirect("exam:grade-list")


def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    if request.method == "POST":
        grade.delete()
        messages.success(request, "Grade deleted successfully.")
    return redirect("exam:grade-list")


def exam_schedule_list(request):
    if request.method == "POST":
        if "add_schedule" in request.POST:
            form = ExamScheduleForm(request.POST)
            if form.is_valid():
                es = form.save(commit=False)
                posted_id = request.POST.get("schedule_id", "").strip()
                if posted_id:
                    es.schedule_id = posted_id
                es.save()
                messages.success(request, "Exam Schedule added successfully.")
            else:
                messages.error(request, "Could not add exam schedule. Please check the form.")
            return redirect("exam:exam-schedule-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                ExamSchedule.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} schedule(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("exam:exam-schedule-list")

    schedules = ExamSchedule.objects.select_related("exam", "school_class", "section", "subject", "room").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_class:
        schedules = schedules.filter(school_class__name=filter_class)
    if filter_section:
        schedules = schedules.filter(section__name=filter_section)
    if filter_status == "active":
        schedules = schedules.filter(status="active")
    elif filter_status == "inactive":
        schedules = schedules.filter(status="inactive")

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        schedules = schedules.order_by("-exam_date", "-start_time")
    elif sort == "recent":
        schedules = schedules.order_by("-updated_at")
    elif sort == "recent_added":
        schedules = schedules.order_by("-created_at")
    else:
        schedules = schedules.order_by("exam_date", "start_time")

    for s in schedules:
        start_minutes = s.start_time.hour * 60 + s.start_time.minute
        end_minutes = s.end_time.hour * 60 + s.end_time.minute
        diff = end_minutes - start_minutes
        if diff < 0:
            diff += 24 * 60
        hours = diff // 60
        minutes = diff % 60
        if hours > 0 and minutes > 0:
            s.duration_str = f"{hours} hr {minutes} min"
        elif hours > 0:
            s.duration_str = f"{hours} hrs"
        else:
            s.duration_str = f"{minutes} min"

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    exams = Exam.objects.all().order_by("-exam_date")
    school_classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.all().order_by("school_class__numeric_order", "name")
    subjects = Subject.objects.all().order_by("name")
    classrooms = ClassRoom.objects.filter(status="active").order_by("room_number")

    return render(request, "portaluser/exam/exam-schedule.html", {
        "schedules": schedules,
        "exams": exams,
        "school_classes": school_classes,
        "sections": sections,
        "subjects": subjects,
        "classrooms": classrooms,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_exam_schedule_id": _generate_exam_schedule_id(),
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_status": filter_status,
    })


def exam_schedule_edit(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)
    if request.method == "POST":
        form = ExamScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            es = form.save(commit=False)
            posted_id = request.POST.get("schedule_id", "").strip()
            if posted_id:
                es.schedule_id = posted_id
            es.save()
            messages.success(request, "Exam Schedule updated successfully.")
        else:
            messages.error(request, "Could not update exam schedule.")
    return redirect("exam:exam-schedule-list")


def exam_schedule_delete(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)
    if request.method == "POST":
        schedule.delete()
        messages.success(request, "Exam Schedule deleted successfully.")
    return redirect("exam:exam-schedule-list")


def _build_exam_attendance_matrix(filter_class="", filter_section="", filter_exam_type="", filter_exam="", sort="asc"):
    """Build the student x subject attendance matrix used by list, print and export views."""
    if sort == "desc":
        student_order = "-name"
    elif sort in ("recent", "recent_added"):
        student_order = "-created_at"
    else:
        student_order = "name"

    if not filter_class or not filter_section:
        first_sec = Section.objects.select_related("school_class").first()
        if first_sec:
            if not filter_class:
                filter_class = first_sec.school_class.name
            if not filter_section:
                filter_section = first_sec.name

    scope = Exam.objects.select_related("school_class", "section", "subject").none()
    matrix_exam = None

    if filter_exam:
        ref_exam = Exam.objects.filter(pk=filter_exam).first()
        if ref_exam:
            matrix_exam = ref_exam
            if not filter_class:
                filter_class = ref_exam.school_class.name
            if not filter_section:
                filter_section = ref_exam.section.name
            scope = Exam.objects.filter(
                school_class=ref_exam.school_class,
                section=ref_exam.section,
            ).filter(name=ref_exam.name)
            if filter_exam_type:
                scope = scope.filter(name=filter_exam_type)
    elif filter_class and filter_section:
        scope = Exam.objects.filter(
            school_class__name=filter_class,
            section__name=filter_section,
        )
        if filter_exam_type:
            scope = scope.filter(name=filter_exam_type)
    else:
        scope = Exam.objects.none()

    scope = scope.order_by("subject__name")

    subject_exam_map = {}
    subjects = []
    for ex in scope:
        if ex.subject and ex.subject.name not in subject_exam_map:
            subject_exam_map[ex.subject.name] = ex.pk
            subjects.append(ex.subject.name)

    if not subjects and filter_class and filter_section:
        sc = SchoolClass.objects.filter(name=filter_class).first()
        sec = Section.objects.filter(school_class=sc, name=filter_section).first() if sc else None
        if sc and sec:
            exam_name = filter_exam_type or "Quarterly Exam"
            all_subjects = Subject.objects.filter(is_active=True)
            for subj in all_subjects:
                ex, _ = Exam.objects.get_or_create(
                    school_class=sc,
                    section=sec,
                    subject=subj,
                    name=exam_name,
                    defaults={
                        "exam_date": "2026-08-01",
                        "start_time": "09:00:00",
                        "end_time": "12:00:00",
                        "total_marks": 100,
                        "pass_marks": 35,
                        "status": "active",
                    }
                )
                if subj.name not in subject_exam_map:
                    subject_exam_map[subj.name] = ex.pk
                    subjects.append(subj.name)

    students = []
    data = {}
    if subjects and filter_class and filter_section:
        students = list(
            Student.objects.filter(
                school_class__name=filter_class,
                section__name=filter_section,
                status="active",
            ).order_by(student_order)
        )
        if not students:
            students = list(Student.objects.filter(status="active").order_by(student_order))

        exam_pks = list(subject_exam_map.values())
        att_qs = ExamAttendance.objects.filter(exam__pk__in=exam_pks).values(
            "student_id", "exam__subject__name", "status"
        )
        for att in att_qs:
            data[(att["student_id"], att["exam__subject__name"])] = att["status"]

    return {
        "subjects": subjects,
        "students": students,
        "data": data,
        "subject_exam_map": subject_exam_map,
        "matrix_exam": matrix_exam,
        "filter_class": filter_class,
        "filter_section": filter_section,
    }


def exam_attendance_list(request):
    if request.method == "POST":
        if "mark_attendance" in request.POST:
            exam_id = request.POST.get("exam")
            if not exam_id:
                messages.error(request, "Please select an exam.")
                return redirect("exam:exam-attendance-list")
            exam = get_object_or_404(Exam, pk=exam_id)
            students = Student.objects.filter(
                school_class=exam.school_class, section=exam.section, status="active"
            )
            for student in students:
                status_key = f"status_{student.pk}"
                remarks_key = f"remarks_{student.pk}"
                status = request.POST.get(status_key, "present")
                remarks = request.POST.get(remarks_key, "")
                ExamAttendance.objects.update_or_create(
                    student=student, exam=exam,
                    defaults={"status": status, "remarks": remarks},
                )
            messages.success(request, "Exam attendance marked successfully.")
            return redirect("exam:exam-attendance-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                ExamAttendance.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} attendance record(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("exam:exam-attendance-list")

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam_type = request.GET.get("filter_exam_type", "").strip()
    filter_exam = request.GET.get("filter_exam", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort = request.GET.get("sort", "asc")

    matrix = _build_exam_attendance_matrix(filter_class, filter_section, filter_exam_type, filter_exam, sort)

    js_matrix_data = {}
    for (sid, subj), status in matrix["data"].items():
        js_matrix_data[f"{sid}_{subj}"] = status

    attendances = ExamAttendance.objects.select_related(
        "student", "exam", "exam__school_class", "exam__section", "exam__subject"
    ).all()
    if matrix["matrix_exam"]:
        attendances = attendances.filter(
            exam__school_class=matrix["matrix_exam"].school_class,
            exam__section=matrix["matrix_exam"].section,
        )
    if filter_exam_type:
        attendances = attendances.filter(exam__name=filter_exam_type)
    if filter_status:
        attendances = attendances.filter(status=filter_status)

    if sort == "desc":
        attendances = attendances.order_by("-student__name")
    elif sort == "recent":
        attendances = attendances.order_by("-updated_at")
    elif sort == "recent_added":
        attendances = attendances.order_by("-created_at")
    else:
        attendances = attendances.order_by("student__name")

    exams = Exam.objects.all().order_by("-exam_date")
    exam_types = list(Exam.objects.values_list("name", flat=True).distinct().order_by("name"))
    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    total_cols = 3 + len(matrix["subjects"])  # checkbox + ID + Name + subjects

    return render(request, "portaluser/exam/exam-attendance.html", {
        "attendances": attendances,
        "exams": exams,
        "exam_types": exam_types,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_exam": filter_exam,
        "filter_class": matrix["filter_class"],
        "filter_section": matrix["filter_section"],
        "filter_exam_type": filter_exam_type,
        "filter_status": filter_status,
        "matrix_subjects": matrix["subjects"],
        "matrix_students": matrix["students"],
        "matrix_data_json": json.dumps(js_matrix_data),
        "subject_exam_map_json": json.dumps(matrix["subject_exam_map"]),
        "matrix_exam": matrix["matrix_exam"],
        "total_cols": total_cols,
        "total_cols_list": range(total_cols),
    })


@require_POST
def exam_attendance_save_ajax(request):
    student_id = request.POST.get("student_id", "").strip()
    exam_id = request.POST.get("exam_id", "").strip()
    status_val = request.POST.get("status", "").strip()
    remarks_val = request.POST.get("remarks", "").strip()

    valid_statuses = dict(ExamAttendance.STATUS_CHOICES)
    if status_val not in valid_statuses:
        return JsonResponse({"success": False, "error": f"Invalid status: {status_val}"}, status=400)
    if not student_id or not exam_id:
        return JsonResponse({"success": False, "error": "student_id and exam_id are required."}, status=400)

    student = Student.objects.filter(pk=student_id, status="active").first()
    exam = Exam.objects.filter(pk=exam_id).first()
    if not student or not exam:
        return JsonResponse({"success": False, "error": "Student or Exam not found."}, status=404)

    rec, created = ExamAttendance.objects.update_or_create(
        student=student,
        exam=exam,
        defaults={"status": status_val, "remarks": remarks_val},
    )
    return JsonResponse({
        "success": True,
        "student_id": student.pk,
        "exam_id": exam.pk,
        "subject": exam.subject.name if exam.subject else "",
        "status": rec.status,
        "remarks": rec.remarks,
        "saved": "new" if created else "updated",
    })


def exam_attendance_edit(request, pk):
    attendance = get_object_or_404(ExamAttendance, pk=pk)
    if request.method == "POST":
        attendance.status = request.POST.get("status", attendance.status)
        attendance.remarks = request.POST.get("remarks", attendance.remarks)
        attendance.save()
        messages.success(request, "Exam attendance updated successfully.")
    return redirect("exam:exam-attendance-list")


def exam_attendance_delete(request, pk):
    attendance = get_object_or_404(ExamAttendance, pk=pk)
    if request.method == "POST":
        attendance.delete()
        messages.success(request, "Exam attendance deleted successfully.")
    return redirect("exam:exam-attendance-list")


def exam_attendance_export_pdf(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam_type = request.GET.get("filter_exam_type", "").strip()
    filter_exam = request.GET.get("filter_exam", "").strip()
    sort = request.GET.get("sort", "asc")

    matrix = _build_exam_attendance_matrix(filter_class, filter_section, filter_exam_type, filter_exam, sort)

    title = "Exam Attendance Report"
    if matrix["matrix_exam"]:
        me = matrix["matrix_exam"]
        title = f"Exam Attendance - {me.name} ({me.school_class.name} - {me.section.name})"
    elif matrix["filter_class"] and matrix["filter_section"]:
        title = f"Exam Attendance - {matrix['filter_class']} - Section {matrix['filter_section']}"
        if filter_exam_type:
            title += f" ({filter_exam_type})"
    elif filter_exam_type:
        title = f"Exam Attendance - {filter_exam_type}"

    js_data = {}
    for (sid, subj), status in matrix["data"].items():
        js_data[f"{sid}_{subj}"] = status

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    context = {
        "title": title,
        "subjects": matrix["subjects"],
        "students": matrix["students"],
        "attendance_data_json": json.dumps(js_data),
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    }
    return render(request, "portaluser/exam/exam-attendance-print.html", context)


def exam_attendance_export_excel(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam_type = request.GET.get("filter_exam_type", "").strip()
    filter_exam = request.GET.get("filter_exam", "").strip()
    sort = request.GET.get("sort", "asc")

    matrix = _build_exam_attendance_matrix(filter_class, filter_section, filter_exam_type, filter_exam, sort)

    filename = "exam_attendance"
    if matrix["matrix_exam"]:
        filename = f"exam_attendance_{matrix['matrix_exam'].exam_id}"
    elif matrix["filter_class"] and matrix["filter_section"]:
        filename = f"exam_attendance_{matrix['filter_class']}_{matrix['filter_section']}"
    elif filter_exam_type:
        filename = f"exam_attendance_{filter_exam_type}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)
    header = ["ID", "Roll No", "Student Name"]
    for subj in matrix["subjects"]:
        header.append(subj)
    writer.writerow(header)

    for student in matrix["students"]:
        row = [
            student.admission_no,
            student.roll_no or "-",
            student.name,
        ]
        for subj in matrix["subjects"]:
            status = matrix["data"].get((student.pk, subj), "-")
            row.append(status.capitalize() if status != "-" else "-")
        writer.writerow(row)

    return response


def _build_exam_results_data(filter_class="", filter_section="", filter_exam="", sort="asc"):
    results_qs = ExamResult.objects.select_related(
        "student", "exam", "exam__school_class", "exam__section", "exam__subject", "grade"
    ).all()

    if filter_class:
        results_qs = results_qs.filter(exam__school_class__name=filter_class)
    if filter_section:
        results_qs = results_qs.filter(exam__section__name=filter_section)
    if filter_exam:
        results_qs = results_qs.filter(exam__pk=filter_exam)

    subjects_list = list(
        Subject.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
    )

    students_map = {}
    for r in results_qs:
        sid = r.student.pk
        if sid not in students_map:
            students_map[sid] = {
                "student": r.student,
                "subjects": {},
                "total_marks": 0,
                "total_obtained": 0,
                "result_pks": [],
                "last_updated_at": r.updated_at,
                "last_created_at": r.created_at,
            }
        subj_name = r.exam.subject.name if r.exam.subject else "Unknown"
        students_map[sid]["subjects"][subj_name] = {
            "marks": r.marks_obtained,
            "total": r.exam.total_marks,
            "pass_marks": r.exam.pass_marks,
            "result_pk": r.pk,
        }
        students_map[sid]["total_marks"] += r.exam.total_marks
        students_map[sid]["total_obtained"] += float(r.marks_obtained)
        students_map[sid]["result_pks"].append(str(r.pk))
        students_map[sid]["last_updated_at"] = max(students_map[sid]["last_updated_at"], r.updated_at)
        students_map[sid]["last_created_at"] = max(students_map[sid]["last_created_at"], r.created_at)

    rows = []
    all_grades = list(Grade.objects.order_by("-min_marks"))
    for sid, data in students_map.items():
        total_marks = data["total_marks"]
        total_obtained = data["total_obtained"]
        percentage = round((total_obtained / total_marks) * 100, 1) if total_marks > 0 else 0
        assigned_grade = None
        for g in all_grades:
            if g.min_marks <= percentage <= g.max_marks:
                assigned_grade = g
                break
        is_pass = all(
            float(v["marks"]) >= v["pass_marks"]
            for v in data["subjects"].values()
        ) if data["subjects"] else False

        subject_marks_list = []
        for subj_name in subjects_list:
            if subj_name in data["subjects"]:
                subject_marks_list.append(data["subjects"][subj_name]["marks"])
            else:
                subject_marks_list.append(None)

        rows.append({
            "student": data["student"],
            "subject_marks_list": subject_marks_list,
            "total_marks": total_marks,
            "total_obtained": total_obtained,
            "percentage": percentage,
            "grade": assigned_grade,
            "is_pass": is_pass,
            "result_pks": ",".join(data["result_pks"]),
            "last_updated_at": data["last_updated_at"],
            "last_created_at": data["last_created_at"],
        })

    if sort == "desc":
        rows.sort(key=lambda x: x["student"].name, reverse=True)
    elif sort == "recent":
        rows.sort(key=lambda x: x["last_updated_at"], reverse=True)
    elif sort == "recent_added":
        rows.sort(key=lambda x: x["last_created_at"], reverse=True)
    else:
        rows.sort(key=lambda x: x["student"].name)

    return {"subjects_list": subjects_list, "results": rows}


def exam_results_list(request):
    if request.method == "POST":
        if "add_result" in request.POST:
            student_id = request.POST.get("student")
            exam_id = request.POST.get("exam")
            student = Student.objects.filter(pk=student_id).first() if student_id else None
            exam = Exam.objects.filter(pk=exam_id).first() if exam_id else None
            if not student or not exam:
                messages.error(request, "Please select a student and an exam.")
                return redirect("exam:exam-results-list")

            remarks = request.POST.get("remarks", "").strip()
            selected_grade_id = request.POST.get("grade", "").strip()

            related_exams = (
                Exam.objects.filter(
                    name=exam.name,
                    school_class=exam.school_class,
                    section=exam.section,
                )
                .select_related("subject")
                .order_by("subject__name")
            )

            exam_by_subject = {
                (rel_exam.subject.name if rel_exam.subject else "Unknown"): rel_exam
                for rel_exam in related_exams
            }

            all_subjects = list(
                Subject.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
            )

            saved_count = 0
            skipped_subjects = []

            for subj_name in all_subjects:
                marks_val = request.POST.get(f"marks_{subj_name}", "").strip()
                if marks_val == "":
                    continue

                rel_exam = exam_by_subject.get(subj_name)
                if not rel_exam:
                    skipped_subjects.append(subj_name)
                    continue

                try:
                    marks = Decimal(marks_val)
                except Exception:
                    messages.error(request, f"Please enter valid marks for {subj_name}.")
                    continue

                grade = None
                if selected_grade_id:
                    grade = Grade.objects.filter(pk=selected_grade_id).first()
                if not grade:
                    total = rel_exam.total_marks
                    percentage = round((float(marks) / total) * 100, 1) if total > 0 else 0
                    for g in Grade.objects.order_by("-min_marks"):
                        if g.min_marks <= percentage <= g.max_marks:
                            grade = g
                            break

                ExamResult.objects.update_or_create(
                    student=student,
                    exam=rel_exam,
                    defaults={"marks_obtained": marks, "grade": grade, "remarks": remarks},
                )
                saved_count += 1

            if skipped_subjects:
                messages.warning(
                    request,
                    "Marks for "
                    + ", ".join(skipped_subjects)
                    + " could not be saved because no exam is scheduled for "
                    + "that subject under this exam name/class/section. "
                    + "Please create a matching Exam entry first.",
                )

            if saved_count > 0:
                messages.success(request, "Exam results saved successfully.")
            elif not skipped_subjects:
                messages.error(request, "Please enter at least one subject's marks.")

            return redirect("exam:exam-results-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                ExamResult.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} result(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("exam:exam-results-list")

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam = request.GET.get("filter_exam", "").strip()
    sort = request.GET.get("sort", "asc")

    data = _build_exam_results_data(filter_class, filter_section, filter_exam, sort)

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    exams = Exam.objects.all().order_by("-exam_date")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    students = Student.objects.filter(status="active").order_by("name")
    grades = Grade.objects.all().order_by("-min_marks")

    return render(request, "portaluser/exam/exam-results.html", {
        "results": data["results"],
        "subjects_list": data["subjects_list"],
        "students": students,
        "exams": exams,
        "grades": grades,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_exam": filter_exam,
    })


def exam_result_subjects(request):
    exam_id = request.GET.get("exam_id")
    student_id = request.GET.get("student_id", "")
    if not exam_id:
        return JsonResponse({"error": "No exam selected."}, status=400)

    ref_exam = Exam.objects.filter(pk=exam_id).select_related("school_class", "section").first()
    if not ref_exam:
        return JsonResponse({"error": "Exam not found."}, status=404)

    related_exams = (
        Exam.objects.filter(
            name=ref_exam.name,
            school_class=ref_exam.school_class,
            section=ref_exam.section,
        )
        .select_related("subject")
        .order_by("subject__name")
    )
    seen_subjects = set()
    exams = []
    for ex in related_exams:
        if ex.subject_id in seen_subjects:
            continue
        seen_subjects.add(ex.subject_id)
        exams.append(ex)

    existing = {}
    if student_id:
        exam_pks = [ex.pk for ex in exams]
        results_qs = ExamResult.objects.filter(student_id=student_id, exam__pk__in=exam_pks)
        for r in results_qs:
            existing[r.exam_id] = {
                "marks": float(r.marks_obtained),
                "remarks": r.remarks,
            }

    subjects = []
    for ex in exams:
        prev = existing.get(ex.pk)
        subjects.append({
            "pk": ex.pk,
            "subject": ex.subject.name if ex.subject else "Unknown",
            "total_marks": ex.total_marks,
            "marks_obtained": prev["marks"] if prev else "",
            "remarks": prev["remarks"] if prev else "",
        })

    return JsonResponse({
        "exam_name": ref_exam.name,
        "class_name": ref_exam.school_class.name,
        "section_name": ref_exam.section.name,
        "subjects": subjects,
    })


def exam_results_export_pdf(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam = request.GET.get("filter_exam", "").strip()
    sort = request.GET.get("sort", "asc")

    data = _build_exam_results_data(filter_class, filter_section, filter_exam, sort)

    title = "Exam Results Report"
    if filter_exam:
        exam = Exam.objects.filter(pk=filter_exam).first()
        if exam:
            title = f"Exam Results - {exam.name} ({exam.school_class.name} - {exam.section.name})"
    elif filter_class and filter_section:
        title = f"Exam Results - {filter_class} - Section {filter_section}"
    elif filter_class:
        title = f"Exam Results - {filter_class}"

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    context = {
        "title": title,
        "results": data["results"],
        "subjects_list": data["subjects_list"],
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    }
    return render(request, "portaluser/exam/exam-results-print.html", context)


def exam_results_export_excel(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam = request.GET.get("filter_exam", "").strip()
    sort = request.GET.get("sort", "asc")

    data = _build_exam_results_data(filter_class, filter_section, filter_exam, sort)

    filename = "exam_results"
    if filter_exam:
        exam = Exam.objects.filter(pk=filter_exam).first()
        if exam:
            filename = f"exam_results_{exam.exam_id}"
    elif filter_class and filter_section:
        filename = f"exam_results_{filter_class}_{filter_section}"
    elif filter_class:
        filename = f"exam_results_{filter_class}"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)
    header = ["Admission No", "Student Name"]
    for subj in data["subjects_list"]:
        header.append(subj)
    header.extend(["Total", "Percent(%)", "Grade", "Result"])
    writer.writerow(header)

    for row in data["results"]:
        line = [row["student"].admission_no, row["student"].name]
        for marks in row["subject_marks_list"]:
            line.append(marks if marks is not None else "-")
        line.extend([
            row["total_obtained"],
            row["percentage"],
            row["grade"].name if row["grade"] else "-",
            "Pass" if row["is_pass"] else "Fail",
        ])
        writer.writerow(line)

    return response


def exam_result_edit(request, pk):
    result = get_object_or_404(ExamResult, pk=pk)
    if request.method == "POST":
        form = ExamResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam result updated successfully.")
        else:
            messages.error(request, "Could not update exam result.")
    return redirect("exam:exam-results-list")


def exam_result_delete(request, pk):
    result = get_object_or_404(ExamResult, pk=pk)
    if request.method == "POST":
        result.delete()
        messages.success(request, "Exam result deleted successfully.")
    return redirect("exam:exam-results-list")


def student_result(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("school_class", "section"),
        pk=pk,
    )

    results = ExamResult.objects.select_related("exam", "grade").filter(student=student).order_by("-exam__exam_date")

    total_marks = 0
    total_obtained = 0
    passed_exams = 0
    for r in results:
        total_marks += r.exam.total_marks
        total_obtained += float(r.marks_obtained)
        if r.is_passed:
            passed_exams += 1

    overall_percentage = round((total_obtained / total_marks) * 100, 1) if total_marks > 0 else 0
    failed_exams = results.count() - passed_exams

    siblings = Student.objects.filter(
        school_class=student.school_class,
        section=student.section,
    ).exclude(pk=student.pk).select_related("school_class", "section")[:5]

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/academics/student-result.html", {
        "student": student,
        "results": results,
        "total_marks": total_marks,
        "total_obtained": total_obtained,
        "overall_percentage": overall_percentage,
        "passed_exams": passed_exams,
        "failed_exams": failed_exams,
        "siblings": siblings,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })
