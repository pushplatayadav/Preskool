import csv
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlencode
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse

from academics.models import SchoolClass, Section, Subject
from people.models import Student, StudentLeave
from core.models import AcademicYear, School
from exam.models import Exam, Grade, ExamResult
from fees.models import Fees


def class_report(request):
    sections = Section.objects.select_related("school_class").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_no_students = request.GET.get("filter_no_students", "").strip()

    if filter_class:
        sections = sections.filter(school_class__name=filter_class)
    if filter_section:
        sections = sections.filter(name=filter_section)
    if filter_no_students:
        try:
            sections = sections.filter(no_of_students=int(filter_no_students))
        except ValueError:
            pass

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        sections = sections.order_by("-school_class__numeric_order", "-name")
    elif sort in ("recent", "recently_viewed", "recently_added", "recent_added"):
        sections = sections.order_by("-pk")
    else:
        sections = sections.order_by("school_class__numeric_order", "name")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    student_count_options = (
        Section.objects.values_list("no_of_students", flat=True)
        .distinct()
        .order_by("no_of_students")
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/report/class-report.html", {
        "sections": sections,
        "class_names": class_names,
        "section_names": section_names,
        "student_count_options": student_count_options,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_no_students": filter_no_students,
    })


def class_report_students(request, pk):
    section = get_object_or_404(Section, pk=pk)
    students = Student.objects.filter(section=section).select_related("school_class", "section")

    students_data = []
    for s in students:
        students_data.append({
            "admission_no": s.admission_no,
            "roll_no": s.roll_no or "-",
            "name": s.name,
            "class_name": s.school_class.name,
            "section": s.section.name,
            "gender": s.get_gender_display(),
            "parent_name": s.parent_name or "-",
            "dob": s.date_of_birth.strftime("%d %b %Y") if s.date_of_birth else "-",
            "status": s.status,
            "profile_image": s.profile_image.url if s.profile_image else "",
            "parent_image": s.parent_image.url if s.parent_image else "",
        })

    return JsonResponse({"students": students_data})


def _filter_report_sections(request):
    sections = Section.objects.select_related("school_class").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_no_students = request.GET.get("filter_no_students", "").strip()

    if filter_class:
        sections = sections.filter(school_class__name=filter_class)
    if filter_section:
        sections = sections.filter(name=filter_section)
    if filter_no_students:
        try:
            sections = sections.filter(no_of_students=int(filter_no_students))
        except ValueError:
            pass

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        sections = sections.order_by("-school_class__numeric_order", "-name")
    elif sort in ("recent", "recently_viewed", "recently_added", "recent_added"):
        sections = sections.order_by("-pk")
    else:
        sections = sections.order_by("school_class__numeric_order", "name")

    return sections, filter_class, filter_section, filter_no_students


def class_report_export_pdf(request):
    sections, filter_class, filter_section, _ = _filter_report_sections(request)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    title = "Class Report"
    if filter_class:
        title += f" - {filter_class}"
    if filter_section:
        title += f" - Section {filter_section}"

    return render(request, "portaluser/report/class-report-print.html", {
        "sections": sections,
        "title": title,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def class_report_export_excel(request):
    sections, filter_class, filter_section, _ = _filter_report_sections(request)

    filename = "class_report"
    if filter_class:
        filename += f"_{filter_class}"
    if filter_section:
        filename += f"_{filter_section}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Class", "Section", "No of Students"])

    for section in sections:
        writer.writerow([
            section.display_id,
            section.school_class.name,
            section.name,
            section.no_of_students,
        ])

    return response


def _filter_report_students(request):
    students = Student.objects.select_related("school_class", "section", "academic_year").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_gender = request.GET.get("filter_gender", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    filter_join_date = request.GET.get("filter_join_date", "").strip()

    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(section__name=filter_section)
    if filter_name:
        students = students.filter(name__icontains=filter_name)
    if filter_gender:
        students = students.filter(gender=filter_gender)
    if filter_status:
        students = students.filter(status=filter_status)
    if filter_join_date:
        try:
            join_date = datetime.strptime(filter_join_date, "%Y-%m-%d").date()
            students = students.filter(admission_date=join_date)
        except ValueError:
            pass

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    elif sort in ("recent", "recently_viewed", "recently_added", "recent_added"):
        students = students.order_by("-pk")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    return students, {
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_name": filter_name,
        "filter_gender": filter_gender,
        "filter_status": filter_status,
        "filter_join_date": filter_join_date,
        "sort": sort,
    }


def student_report(request):
    students, filters = _filter_report_students(request)

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    student_names = Student.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/report/student-report.html", {
        "students": students,
        "class_names": class_names,
        "section_names": section_names,
        "student_names": student_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        **filters,
    })


def student_report_export_pdf(request):
    students, filters = _filter_report_students(request)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    title = "Student Report"
    if filters["filter_class"]:
        title += f" - {filters['filter_class']}"
    if filters["filter_section"]:
        title += f" - Section {filters['filter_section']}"

    return render(request, "portaluser/report/student-report-print.html", {
        "students": students,
        "title": title,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def student_report_export_excel(request):
    students, filters = _filter_report_students(request)

    filename = "student_report"
    if filters["filter_class"]:
        filename += f"_{filters['filter_class']}"
    if filters["filter_section"]:
        filename += f"_{filters['filter_section']}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Admission No", "Roll No", "Name", "Class", "Section", "Gender",
        "Parent", "Date of Join", "DOB", "Status",
    ])

    for student in students:
        parent_name = student.parent_name or student.father_name or student.mother_name or "-"
        join_date = student.admission_date or (student.created_at.date() if student.created_at else None)
        dob = student.date_of_birth
        writer.writerow([
            student.admission_no,
            student.roll_no or "-",
            student.name,
            student.school_class.name,
            student.section.name,
            student.get_gender_display(),
            parent_name,
            join_date.strftime("%d %b %Y") if join_date else "-",
            dob.strftime("%d %b %Y") if dob else "-",
            student.get_status_display(),
        ])

    return response


def _build_grade_report_data(filter_class="", filter_section="", filter_exam_type="", sort="asc"):
    """Build the student x subject marks matrix used by list, print and export views."""
    results_qs = ExamResult.objects.select_related(
        "student", "exam", "exam__school_class", "exam__section", "exam__subject", "grade"
    ).all()

    if filter_class:
        results_qs = results_qs.filter(exam__school_class__name=filter_class)
    if filter_section:
        results_qs = results_qs.filter(exam__section__name=filter_section)
    if filter_exam_type:
        results_qs = results_qs.filter(exam__name=filter_exam_type)

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
                "last_updated_at": r.updated_at,
                "last_created_at": r.created_at,
            }
        subj_name = r.exam.subject.name if r.exam.subject else "Unknown"
        students_map[sid]["subjects"][subj_name] = {
            "marks": r.marks_obtained,
            "total": r.exam.total_marks,
            "pass_marks": r.exam.pass_marks,
        }
        students_map[sid]["total_marks"] += r.exam.total_marks
        students_map[sid]["total_obtained"] += float(r.marks_obtained)
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

        subject_marks_list = []
        subject_pass_marks_list = []
        subject_total_marks_list = []
        subject_details = []
        for subj_name in subjects_list:
            if subj_name in data["subjects"]:
                subj = data["subjects"][subj_name]
                subject_marks_list.append(subj["marks"])
                subject_pass_marks_list.append(subj["pass_marks"])
                subject_total_marks_list.append(subj["total"])
                subject_details.append(subj)
            else:
                subject_marks_list.append(None)
                subject_pass_marks_list.append(None)
                subject_total_marks_list.append(None)
                subject_details.append(None)

        rows.append({
            "student": data["student"],
            "subject_marks_list": subject_marks_list,
            "subject_pass_marks_list": subject_pass_marks_list,
            "subject_total_marks_list": subject_total_marks_list,
            "subject_details": subject_details,
            "total_marks": total_marks,
            "total_obtained": total_obtained,
            "percentage": percentage,
            "grade": assigned_grade,
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


def grade_report(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam_type = request.GET.get("filter_exam_type", "").strip()
    sort = request.GET.get("sort", "asc")

    data = _build_grade_report_data(filter_class, filter_section, filter_exam_type, sort)

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    exam_types = Exam.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/report/grade-report.html", {
        "results": data["results"],
        "subjects_list": data["subjects_list"],
        "class_names": class_names,
        "section_names": section_names,
        "exam_types": exam_types,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_exam_type": filter_exam_type,
    })


def grade_report_export_pdf(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam_type = request.GET.get("filter_exam_type", "").strip()
    sort = request.GET.get("sort", "asc")

    data = _build_grade_report_data(filter_class, filter_section, filter_exam_type, sort)

    title = "Grade Report"
    if filter_exam_type:
        title += f" - {filter_exam_type}"
    if filter_class:
        title += f" - {filter_class}"
    if filter_section:
        title += f" - Section {filter_section}"

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/report/grade-report-print.html", {
        "title": title,
        "results": data["results"],
        "subjects_list": data["subjects_list"],
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def grade_report_export_excel(request):
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_exam_type = request.GET.get("filter_exam_type", "").strip()
    sort = request.GET.get("sort", "asc")

    data = _build_grade_report_data(filter_class, filter_section, filter_exam_type, sort)

    filename = "grade_report"
    if filter_exam_type:
        filename += f"_{filter_exam_type}"
    if filter_class:
        filename += f"_{filter_class}"
    if filter_section:
        filename += f"_{filter_section}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    header = ["Admission No", "Student Name"]
    for subj in data["subjects_list"]:
        header.append(subj)
    header.extend(["Total", "Percent(%)", "Grade"])
    writer.writerow(header)

    for row in data["results"]:
        line = [row["student"].admission_no, row["student"].name]
        for marks in row["subject_marks_list"]:
            line.append(marks if marks is not None else "-")
        line.extend([
            row["total_obtained"],
            row["percentage"],
            row["grade"].name if row["grade"] else "-",
        ])
        writer.writerow(line)

    return response


# ---------------------------------------------------------------------------
# Leave Report
# ---------------------------------------------------------------------------

# Default quota (in days) granted for each leave type. Derived from the
# values used across the student leave module; the report header shows these.
LEAVE_QUOTA_MAP = {
    "medical": 10,
    "casual": 12,
    "maternity": 10,
    "paternity": 10,
    "special": 10,
}


def _leave_type_options():
    """Return the leave type columns dynamically from the StudentLeave model."""
    options = []
    for value, label in StudentLeave.LEAVE_TYPE_CHOICES:
        options.append({
            "value": value,
            "name": label,
            "quota": LEAVE_QUOTA_MAP.get(value, 10),
        })
    return options


def _filtered_students_for_leave_report(request):
    students = Student.objects.select_related(
        "school_class", "section", "academic_year"
    ).all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()

    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(section__name=filter_section)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        students = students.order_by(
            "-school_class__numeric_order", "-section__name", "-roll_no"
        )
    elif sort in ("recent", "recently_viewed"):
        students = students.order_by("-pk")
    elif sort == "recent_added":
        students = students.order_by("-created_at")
    else:
        students = students.order_by(
            "school_class__numeric_order", "section__name", "roll_no"
        )

    return students, filter_class, filter_section, sort


def _build_leave_report_data(request):
    """Build the student x leave-type matrix shared by list, print and export."""
    students, filter_class, filter_section, sort = _filtered_students_for_leave_report(request)

    leave_types = _leave_type_options()

    approved_leaves = (
        StudentLeave.objects.filter(status="approved")
        .values_list("student_id", "leave_type")
    )
    used_map = {}
    for student_id, leave_type in approved_leaves:
        key = (student_id, leave_type)
        used_map[key] = used_map.get(key, 0) + 1

    rows = []
    for student in students:
        student_leave_columns = []
        for lt in leave_types:
            used = used_map.get((student.pk, lt["value"]), 0)
            quota = lt["quota"]
            available = max(0, quota - used)
            student_leave_columns.append({
                "used": used,
                "available": available,
                "quota": quota,
            })
        rows.append({"student": student, "leaves": student_leave_columns})

    return {
        "rows": rows,
        "leave_types": leave_types,
        "leave_colspan": 2 + len(leave_types) * 2,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "sort": sort,
    }


def leave_report(request):
    data = _build_leave_report_data(request)

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/report/leave-report.html", {
        "rows": data["rows"],
        "leave_types": data["leave_types"],
        "leave_colspan": data["leave_colspan"],
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": data["sort"],
        "filter_class": data["filter_class"],
        "filter_section": data["filter_section"],
    })


def leave_report_export_pdf(request):
    data = _build_leave_report_data(request)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    title = "Leave Report"
    if data["filter_class"]:
        title += f" - {data['filter_class']}"
    if data["filter_section"]:
        title += f" - Section {data['filter_section']}"

    return render(request, "portaluser/report/leave-report-print.html", {
        "title": title,
        "rows": data["rows"],
        "leave_types": data["leave_types"],
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def leave_report_export_excel(request):
    data = _build_leave_report_data(request)

    filename = "leave_report"
    if data["filter_class"]:
        filename += f"_{data['filter_class']}"
    if data["filter_section"]:
        filename += f"_{data['filter_section']}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)

    header = ["Admission No", "Student Name", "Roll No"]
    for lt in data["leave_types"]:
        header.append(f"{lt['name']} ({lt['quota']}) - Used")
        header.append(f"{lt['name']} ({lt['quota']}) - Available")
    writer.writerow(header)

    for row in data["rows"]:
        line = [
            row["student"].admission_no,
            row["student"].name,
            row["student"].roll_no or "-",
        ]
        for lv in row["leaves"]:
            line.append(lv["used"])
            line.append(lv["available"])
        writer.writerow(line)

    return response


# ---------------------------------------------------------------------------
# Fees Report
# ---------------------------------------------------------------------------

def _filter_fees_report(request):
    """Apply the Class / Section / Student / Year / Sort filters to the Fees rows."""
    fees = Fees.objects.select_related(
        "student", "student__school_class", "student__section",
        "fees_group", "fees_type", "academic_year",
    ).all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_student = request.GET.get("filter_student", "").strip()
    year_filter = request.GET.get("year", "").strip()

    if filter_class:
        fees = fees.filter(student__school_class__name=filter_class)
    if filter_section:
        fees = fees.filter(student__section__name=filter_section)
    if filter_student:
        fees = fees.filter(student__name__icontains=filter_student)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    if year_filter:
        fees = fees.filter(academic_year__name=year_filter)
    elif current_academic_year:
        fees = fees.filter(academic_year=current_academic_year)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        fees = fees.order_by("-student__name", "due_date")
    elif sort in ("recent", "recently_viewed"):
        fees = fees.order_by("-updated_at")
    elif sort == "recent_added":
        fees = fees.order_by("-created_at")
    else:
        fees = fees.order_by("student__name", "due_date")

    return fees, {
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_student": filter_student,
        "year_filter": year_filter,
        "sort": sort,
    }


def _fees_report_rows(fees):
    """Build the fee rows with a computed balance and running totals."""
    rows = []
    total_amount = Decimal("0")
    total_discount = Decimal("0")
    total_fine = Decimal("0")
    total_balance = Decimal("0")

    for fee in fees:
        if fee.status == "paid":
            balance = Decimal("0")
        else:
            balance = (fee.amount + fee.fine) - fee.discount
            if balance < 0:
                balance = Decimal("0")
        total_amount += fee.amount
        total_discount += fee.discount
        total_fine += fee.fine
        total_balance += balance
        rows.append({"fee": fee, "balance": balance})

    return rows, {
        "amount": total_amount,
        "discount": total_discount,
        "fine": total_fine,
        "balance": total_balance,
    }


def fees_report(request):
    fees, filters = _filter_fees_report(request)
    rows, totals = _fees_report_rows(fees)

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    student_names = Student.objects.values_list("name", flat=True).distinct().order_by("name")
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    preserved = {}
    if filters["filter_class"]:
        preserved["filter_class"] = filters["filter_class"]
    if filters["filter_section"]:
        preserved["filter_section"] = filters["filter_section"]
    if filters["filter_student"]:
        preserved["filter_student"] = filters["filter_student"]
    base_query = urlencode(preserved)

    return render(request, "portaluser/report/fees-report.html", {
        "rows": rows,
        "totals": totals,
        "class_names": class_names,
        "section_names": section_names,
        "student_names": student_names,
        "academic_years": academic_years,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "base_query": base_query,
        **filters,
    })


def fees_report_export_pdf(request):
    fees, filters = _filter_fees_report(request)
    rows, totals = _fees_report_rows(fees)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    title = "Fees Report"
    if filters["filter_class"]:
        title += f" - {filters['filter_class']}"
    if filters["filter_section"]:
        title += f" - Section {filters['filter_section']}"

    return render(request, "portaluser/report/fees-report-print.html", {
        "rows": rows,
        "totals": totals,
        "title": title,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def fees_report_export_excel(request):
    fees, filters = _filter_fees_report(request)
    rows, totals = _fees_report_rows(fees)

    filename = "fees_report"
    if filters["filter_class"]:
        filename += f"_{filters['filter_class']}"
    if filters["filter_section"]:
        filename += f"_{filters['filter_section']}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Fees Group", "Fees Code", "Due Date", "Amount", "Status",
        "Ref ID", "Mode", "Date Paid", "Discount", "Fine", "Balance",
    ])

    for row in rows:
        fee = row["fee"]
        writer.writerow([
            fee.fees_group.name if fee.fees_group else "-",
            fee.fees_code or "-",
            fee.due_date.strftime("%d %b %Y") if fee.due_date else "-",
            fee.amount,
            fee.get_status_display(),
            fee.ref_id or "-",
            fee.get_payment_mode_display() if fee.payment_mode else "-",
            fee.date_paid.strftime("%d %b %Y") if fee.date_paid else "-",
            fee.discount,
            fee.fine,
            row["balance"],
        ])

    writer.writerow([])
    writer.writerow(["", "", "", totals["amount"], "", "", "", "", totals["discount"], totals["fine"], totals["balance"]])

    return response
