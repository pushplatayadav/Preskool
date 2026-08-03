import csv
import json
from datetime import datetime, date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import Student, StudentLeave, StudentAttendance, Teacher, Staff, TeacherAttendance, StaffAttendance
from academics.models import SchoolClass, Section, Subject
from core.models import AcademicYear, School


def student_grid(request):
    students = Student.objects.select_related("school_class", "section", "academic_year").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_gender = request.GET.get("filter_gender", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

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

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST" and "delete_student" in request.POST:
        pk = request.POST.get("student_id")
        if pk:
            try:
                student = get_object_or_404(Student, pk=pk)
                student.delete()
                messages.success(request, "Student deleted successfully.")
            except Exception:
                messages.error(request, "Error deleting student.")
        else:
            messages.error(request, "No student ID provided.")
        return redirect("people:student-grid")

    return render(request, "portaluser/people/student-grid.html", {
        "students": students,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_name": filter_name,
        "filter_gender": filter_gender,
        "filter_status": filter_status,
    })


def student_list(request):
    students = Student.objects.select_related("school_class", "section", "academic_year").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_gender = request.GET.get("filter_gender", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

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

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST":
        if "delete_student" in request.POST:
            pk = request.POST.get("student_id")
            if pk:
                try:
                    student = get_object_or_404(Student, pk=pk)
                    student.delete()
                    messages.success(request, "Student deleted successfully.")
                except Exception:
                    messages.error(request, "Error deleting student.")
            else:
                messages.error(request, "No student ID provided.")
            return redirect("people:student-list")
        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("student_ids")
            if ids:
                Student.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} student(s) deleted successfully.")
            return redirect("people:student-list")

    return render(request, "portaluser/people/students.html", {
        "students": students,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_name": filter_name,
        "filter_gender": filter_gender,
        "filter_status": filter_status,
    })


def add_student_page(request):
    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST":
        try:
            name = " ".join(filter(None, [request.POST.get("first_name", ""), request.POST.get("last_name", "")]))
            if not name:
                messages.error(request, "First Name and Last Name are required.")
                return render(request, "portaluser/people/add-student.html", {
                    "class_names": class_names,
                    "section_names": section_names,
                    "current_academic_year": current_academic_year,
                    "academic_years": academic_years,
                    "school_name": school.name if school else "Global International",
                })

            school_class = get_object_or_404(SchoolClass, name=request.POST.get("school_class"))
            section = get_object_or_404(Section, school_class=school_class, name=request.POST.get("section"))
            academic_year_id = request.POST.get("academic_year")
            academic_year = None
            if academic_year_id:
                academic_year = AcademicYear.objects.filter(pk=academic_year_id).first()
            if not academic_year:
                academic_year = AcademicYear.objects.filter(is_current=True).first()

            dob_str = request.POST.get("date_of_birth", "")
            date_of_birth = None
            if dob_str:
                for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                    try:
                        date_of_birth = datetime.strptime(dob_str, fmt).date()
                        break
                    except ValueError:
                        continue

            admission_date_str = request.POST.get("admission_date", "")
            admission_date = None
            if admission_date_str:
                for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                    try:
                        admission_date = datetime.strptime(admission_date_str, fmt).date()
                        break
                    except ValueError:
                        continue

            languages = request.POST.getlist("languages_known")
            languages_known = ", ".join(languages)

            student = Student(
                admission_no=request.POST.get("admission_no", ""),
                roll_no=request.POST.get("roll_no", ""),
                name=name,
                school_class=school_class,
                section=section,
                gender=request.POST.get("gender", "male"),
                date_of_birth=date_of_birth,
                status=request.POST.get("status", "active"),
                academic_year=academic_year,
                # Additional Personal Information
                admission_date=admission_date,
                blood_group=request.POST.get("blood_group", ""),
                house=request.POST.get("house", ""),
                religion=request.POST.get("religion", ""),
                category=request.POST.get("category", ""),
                primary_contact_number=request.POST.get("primary_contact_number", ""),
                email=request.POST.get("email", ""),
                caste=request.POST.get("caste", ""),
                mother_tongue=request.POST.get("mother_tongue", ""),
                languages_known=languages_known,
                # Father's Information
                father_name=request.POST.get("father_name", ""),
                father_email=request.POST.get("father_email", ""),
                father_phone=request.POST.get("father_phone", ""),
                father_occupation=request.POST.get("father_occupation", ""),
                # Mother's Information
                mother_name=request.POST.get("mother_name", ""),
                mother_email=request.POST.get("mother_email", ""),
                mother_phone=request.POST.get("mother_phone", ""),
                mother_occupation=request.POST.get("mother_occupation", ""),
                # Guardian Information
                guardian_is=request.POST.get("guardian_is", ""),
                guardian_name=request.POST.get("guardian_name", ""),
                guardian_relation=request.POST.get("guardian_relation", ""),
                guardian_phone=request.POST.get("guardian_phone", ""),
                guardian_email=request.POST.get("guardian_email", ""),
                guardian_occupation=request.POST.get("guardian_occupation", ""),
                guardian_address=request.POST.get("guardian_address", ""),
                # Sibling Information
                has_sibling_in_school=request.POST.get("has_sibling_in_school") == "yes",
                sibling_name=request.POST.get("sibling_name", ""),
                sibling_roll_no=request.POST.get("sibling_roll_no", ""),
                sibling_admission_no=request.POST.get("sibling_admission_no", ""),
                sibling_class=request.POST.get("sibling_class", ""),
                # Address
                current_address=request.POST.get("current_address", ""),
                permanent_address=request.POST.get("permanent_address", ""),
                # Transport
                route=request.POST.get("route", ""),
                vehicle_number=request.POST.get("vehicle_number", ""),
                pickup_point=request.POST.get("pickup_point", ""),
                # Hostel
                hostel=request.POST.get("hostel", ""),
                room_no=request.POST.get("room_no", ""),
                # Medical History
                medical_condition=request.POST.get("medical_condition", ""),
                allergies=request.POST.get("allergies", ""),
                medications=request.POST.get("medications", ""),
                # Previous School
                previous_school_name=request.POST.get("previous_school_name", ""),
                previous_school_address=request.POST.get("previous_school_address", ""),
                previous_school_other_details=request.POST.get("previous_school_other_details", ""),
                # Bank Details
                bank_name=request.POST.get("bank_name", ""),
                bank_branch=request.POST.get("bank_branch", ""),
                ifsc_number=request.POST.get("ifsc_number", ""),
                # Other Information
                other_information=request.POST.get("other_information", ""),
            )

            if request.FILES.get("profile_image"):
                student.profile_image = request.FILES["profile_image"]
            if request.FILES.get("father_image"):
                student.father_image = request.FILES["father_image"]
            if request.FILES.get("mother_image"):
                student.mother_image = request.FILES["mother_image"]
            if request.FILES.get("guardian_image"):
                student.guardian_image = request.FILES["guardian_image"]
            if request.FILES.get("medical_document"):
                student.medical_document = request.FILES["medical_document"]
            if request.FILES.get("transfer_certificate"):
                student.transfer_certificate = request.FILES["transfer_certificate"]

            student.save()
            messages.success(request, f"Student {student.name} added successfully.")
            return redirect("people:student-grid")
        except Http404:
            messages.error(request, "Selected class or section not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "portaluser/people/add-student.html", {
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
    })


def edit_student_page(request, pk):
    student = get_object_or_404(Student, pk=pk)
    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()
    languages = [lang.strip() for lang in student.languages_known.split(",") if lang.strip()]
    allergies_list = [a.strip() for a in student.allergies.split(",") if a.strip()]
    medications_list = [m.strip() for m in student.medications.split(",") if m.strip()]

    name_parts = student.name.split(maxsplit=1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    if request.method == "POST":
        try:
            name = " ".join(filter(None, [request.POST.get("first_name", ""), request.POST.get("last_name", "")]))
            if not name:
                messages.error(request, "First Name and Last Name are required.")
                return render(request, "portaluser/people/edit-student.html", {
                    "student": student,
                    "class_names": class_names,
                    "section_names": section_names,
                    "current_academic_year": current_academic_year,
                    "academic_years": academic_years,
                    "school_name": school.name if school else "Global International",
                    "languages": languages,
                    "allergies_list": allergies_list,
                    "medications_list": medications_list,
                    "first_name": first_name,
                    "last_name": last_name,
                })

            school_class = get_object_or_404(SchoolClass, name=request.POST.get("school_class"))
            section = get_object_or_404(Section, school_class=school_class, name=request.POST.get("section"))
            academic_year_id = request.POST.get("academic_year")
            academic_year = None
            if academic_year_id:
                academic_year = AcademicYear.objects.filter(pk=academic_year_id).first()
            if not academic_year:
                academic_year = AcademicYear.objects.filter(is_current=True).first()

            dob_str = request.POST.get("date_of_birth", "")
            date_of_birth = None
            if dob_str:
                for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                    try:
                        date_of_birth = datetime.strptime(dob_str, fmt).date()
                        break
                    except ValueError:
                        continue

            admission_date_str = request.POST.get("admission_date", "")
            admission_date = None
            if admission_date_str:
                for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                    try:
                        admission_date = datetime.strptime(admission_date_str, fmt).date()
                        break
                    except ValueError:
                        continue

            languages_known_str = request.POST.get("languages_known", "")

            student.admission_no = request.POST.get("admission_no", student.admission_no)
            student.roll_no = request.POST.get("roll_no", student.roll_no)
            student.name = name
            student.school_class = school_class
            student.section = section
            student.gender = request.POST.get("gender", "male")
            student.date_of_birth = date_of_birth
            student.status = request.POST.get("status", "active")
            student.academic_year = academic_year
            student.admission_date = admission_date
            student.blood_group = request.POST.get("blood_group", "")
            student.house = request.POST.get("house", "")
            student.religion = request.POST.get("religion", "")
            student.category = request.POST.get("category", "")
            student.primary_contact_number = request.POST.get("primary_contact_number", "")
            student.email = request.POST.get("email", "")
            student.caste = request.POST.get("caste", "")
            student.mother_tongue = request.POST.get("mother_tongue", "")
            student.languages_known = languages_known_str
            student.father_name = request.POST.get("father_name", "")
            student.father_email = request.POST.get("father_email", "")
            student.father_phone = request.POST.get("father_phone", "")
            student.father_occupation = request.POST.get("father_occupation", "")
            student.mother_name = request.POST.get("mother_name", "")
            student.mother_email = request.POST.get("mother_email", "")
            student.mother_phone = request.POST.get("mother_phone", "")
            student.mother_occupation = request.POST.get("mother_occupation", "")
            student.guardian_is = request.POST.get("guardian_is", "")
            student.guardian_name = request.POST.get("guardian_name", "")
            student.guardian_relation = request.POST.get("guardian_relation", "")
            student.guardian_phone = request.POST.get("guardian_phone", "")
            student.guardian_email = request.POST.get("guardian_email", "")
            student.guardian_occupation = request.POST.get("guardian_occupation", "")
            student.guardian_address = request.POST.get("guardian_address", "")
            student.has_sibling_in_school = request.POST.get("has_sibling_in_school") == "yes"
            student.sibling_name = request.POST.get("sibling_name", "")
            student.sibling_roll_no = request.POST.get("sibling_roll_no", "")
            student.sibling_admission_no = request.POST.get("sibling_admission_no", "")
            student.sibling_class = request.POST.get("sibling_class", "")
            student.current_address = request.POST.get("current_address", "")
            student.permanent_address = request.POST.get("permanent_address", "")
            student.route = request.POST.get("route", "")
            student.vehicle_number = request.POST.get("vehicle_number", "")
            student.pickup_point = request.POST.get("pickup_point", "")
            student.hostel = request.POST.get("hostel", "")
            student.room_no = request.POST.get("room_no", "")
            student.medical_condition = request.POST.get("medical_condition", "")
            allergies_raw = request.POST.get("allergies", "")
            student.allergies = ", ".join([a.strip() for a in allergies_raw.split(",") if a.strip()])
            medications_raw = request.POST.get("medications", "")
            student.medications = ", ".join([m.strip() for m in medications_raw.split(",") if m.strip()])
            student.previous_school_name = request.POST.get("previous_school_name", "")
            student.previous_school_address = request.POST.get("previous_school_address", "")
            student.previous_school_other_details = request.POST.get("previous_school_other_details", "")
            student.bank_name = request.POST.get("bank_name", "")
            student.bank_branch = request.POST.get("bank_branch", "")
            student.ifsc_number = request.POST.get("ifsc_number", "")
            student.other_information = request.POST.get("other_information", "")

            if request.FILES.get("profile_image"):
                student.profile_image = request.FILES["profile_image"]
            if request.FILES.get("father_image"):
                student.father_image = request.FILES["father_image"]
            if request.FILES.get("mother_image"):
                student.mother_image = request.FILES["mother_image"]
            if request.FILES.get("guardian_image"):
                student.guardian_image = request.FILES["guardian_image"]
            if request.FILES.get("medical_document"):
                student.medical_document = request.FILES["medical_document"]
            if request.FILES.get("transfer_certificate"):
                student.transfer_certificate = request.FILES["transfer_certificate"]

            student.save()
            messages.success(request, f"Student {student.name} updated successfully.")
            return redirect("people:student-list")
        except Http404:
            messages.error(request, "Selected class or section not found.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "portaluser/people/edit-student.html", {
        "student": student,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "languages": languages,
        "allergies_list": allergies_list,
        "medications_list": medications_list,
        "first_name": first_name,
        "last_name": last_name,
    })


def student_details_redirect(request):
    student = Student.objects.first()
    if student:
        return redirect("people:student-details", pk=student.pk)
    return redirect("people:student-list")


def student_details(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("school_class", "section", "academic_year"),
        pk=pk,
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    languages = [lang.strip() for lang in student.languages_known.split(",") if lang.strip()]

    return render(request, "portaluser/people/student-details.html", {
        "student": student,
        "languages": languages,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
    })


def student_promotion(request):
    from exam.models import ExamResult

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.all().order_by("school_class__numeric_order", "name")

    from_class = request.GET.get("from_class", "")
    from_section = request.GET.get("from_section", "")
    to_class = request.GET.get("to_class", "")
    to_section = request.GET.get("to_section", "")
    to_session = request.GET.get("to_session", "")

    to_session_name = ""
    if to_session:
        try:
            to_session_obj = AcademicYear.objects.get(name=to_session)
            to_session_name = to_session_obj.name
        except AcademicYear.DoesNotExist:
            pass

    to_sections = []
    if to_class:
        to_sections = Section.objects.filter(school_class__name=to_class).order_by("name")

    students = []
    if from_class and from_section:
        students = Student.objects.filter(
            school_class__name=from_class,
            section__name=from_section,
            status="active",
        ).select_related("school_class", "section").order_by("roll_no", "name")

        all_results = ExamResult.objects.filter(student__in=students).select_related("exam")
        student_pass_map = {}
        for r in all_results:
            sid = r.student_id
            if sid not in student_pass_map:
                student_pass_map[sid] = False
            if float(r.marks_obtained) >= r.exam.pass_marks:
                student_pass_map[sid] = True

        for s in students:
            s.result_status = "pass" if student_pass_map.get(s.pk) else "fail" if s.pk in student_pass_map else "nograde"
            s.promotion_action = ""

    if request.method == "POST" and "promote_students" in request.POST:
        import json
        from_class = request.POST.get("from_class", "")
        from_section = request.POST.get("from_section", "")
        to_class_name = request.POST.get("to_class", "")
        to_section_name = request.POST.get("to_section", "")
        to_session_id = request.POST.get("to_session", "")
        promotion_data_raw = request.POST.get("promotion_data", "[]")

        try:
            promotion_ids = json.loads(promotion_data_raw)
        except (json.JSONDecodeError, TypeError):
            promotion_ids = []

        if not promotion_ids:
            messages.warning(request, "No students selected for promotion.")
        else:
            promoted_count = 0
            to_session_obj = None
            if to_session_id:
                try:
                    to_session_obj = AcademicYear.objects.get(name=to_session_id)
                except AcademicYear.DoesNotExist:
                    try:
                        to_session_obj = AcademicYear.objects.get(pk=to_session_id)
                    except AcademicYear.DoesNotExist:
                        pass

            to_class_obj = None
            to_section_obj = None
            if to_class_name:
                to_class_obj = SchoolClass.objects.filter(name=to_class_name).first()
            if to_section_name and to_class_obj:
                to_section_obj = Section.objects.filter(school_class=to_class_obj, name=to_section_name).first()

            if not to_class_obj or not to_section_obj:
                messages.error(request, "Target class or section not found.")
                return redirect("people:student-promotion")

            for sid in promotion_ids:
                try:
                    student = Student.objects.get(pk=sid)
                    student.school_class = to_class_obj
                    student.section = to_section_obj
                    if to_session_obj:
                        student.academic_year = to_session_obj
                    student.save()
                    promoted_count += 1
                except Student.DoesNotExist:
                    continue

            messages.success(request, f"{promoted_count} student(s) promoted successfully to {to_class_name} - Section {to_section_name}.")
            return redirect("people:student-promotion")

    return render(request, "portaluser/people/student-promotion.html", {
        "classes": classes,
        "sections": sections,
        "to_sections": to_sections,
        "students": students,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "from_class": from_class,
        "from_section": from_section,
        "to_class": to_class,
        "to_section": to_section,
        "to_session": to_session,
        "to_session_name": to_session_name,
    })


def student_leaves(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("school_class", "section", "academic_year"),
        pk=pk,
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    languages = [lang.strip() for lang in student.languages_known.split(",") if lang.strip()]

    leaves = StudentLeave.objects.filter(student=student)
    attendance = StudentAttendance.objects.filter(student=student, academic_year=current_academic_year)

    leave_types = ["medical", "casual", "maternity", "paternity"]
    leave_quotas = {}
    for lt in leave_types:
        used = leaves.filter(leave_type=lt, status="approved").count()
        quota = {"medical": 10, "casual": 12, "maternity": 10, "paternity": 0}.get(lt, 0)
        leave_quotas[lt] = {"used": used, "available": max(0, quota - used), "total": quota}

    total_present = attendance.filter(status="present").count()
    total_absent = attendance.filter(status="absent").count()
    total_half_day = attendance.filter(status="half_day").count()
    total_late = attendance.filter(status="late").count()

    attendance_dict = {}
    for rec in attendance:
        attendance_dict[f"{rec.date.day}_{rec.date.month}"] = rec.status

    month_info = [
        {"index": 0, "name": "Jun", "number": 6},
        {"index": 1, "name": "Jul", "number": 7},
        {"index": 2, "name": "Aug", "number": 8},
        {"index": 3, "name": "Sep", "number": 9},
        {"index": 4, "name": "Oct", "number": 10},
        {"index": 5, "name": "Nov", "number": 11},
        {"index": 6, "name": "Dec", "number": 12},
        {"index": 7, "name": "Jan", "number": 1},
        {"index": 8, "name": "Feb", "number": 2},
        {"index": 9, "name": "Mar", "number": 3},
        {"index": 10, "name": "Apr", "number": 4},
    ]
    day_range = range(1, 32)

    attendance_grid = []
    for day in range(1, 32):
        row = []
        for m in month_info:
            row.append(attendance_dict.get(f"{day}_{m['number']}", ""))
        attendance_grid.append(row)

    if request.method == "POST":
        if "apply_leave" in request.POST:
            try:
                leave_type = request.POST.get("leave_type")
                from_date_str = request.POST.get("from_date")
                to_date_str = request.POST.get("to_date")
                no_of_days = request.POST.get("no_of_days", 1)
                reason = request.POST.get("reason", "")
                leave_days_type = request.POST.get("leave_days_type", "full")

                from_date = None
                if from_date_str:
                    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
                        try:
                            from_date = datetime.strptime(from_date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                to_date = None
                if to_date_str:
                    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
                        try:
                            to_date = datetime.strptime(to_date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                StudentLeave.objects.create(
                    student=student,
                    leave_type=leave_type,
                    from_date=from_date or date.today(),
                    to_date=to_date or date.today(),
                    no_of_days=int(no_of_days),
                    leave_days_type=leave_days_type,
                    reason=reason,
                    status="pending",
                )
                messages.success(request, "Leave applied successfully.")
            except Exception as e:
                messages.error(request, f"Error applying leave: {str(e)}")
            return redirect("people:student-leaves", pk=student.pk)

        elif "mark_attendance" in request.POST:
            try:
                attendance_date_str = request.POST.get("attendance_date")
                attendance_status = request.POST.get("attendance_status")
                attendance_date = None
                if attendance_date_str:
                    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
                        try:
                            attendance_date = datetime.strptime(attendance_date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                if attendance_date:
                    StudentAttendance.objects.update_or_create(
                        student=student,
                        date=attendance_date,
                        defaults={
                            "status": attendance_status,
                            "academic_year": current_academic_year,
                        },
                    )
                    messages.success(request, "Attendance marked successfully.")
            except Exception as e:
                messages.error(request, f"Error marking attendance: {str(e)}")
            return redirect("people:student-leaves", pk=student.pk)

        elif "cancel_leave" in request.POST:
            leave_id = request.POST.get("leave_id")
            if leave_id:
                StudentLeave.objects.filter(pk=leave_id, student=student, status="pending").delete()
                messages.success(request, "Leave request cancelled.")
            return redirect("people:student-leaves", pk=student.pk)

    return render(request, "portaluser/people/student-leaves.html", {
        "student": student,
        "languages": languages,
        "leaves": leaves,
        "attendance": attendance,
        "attendance_dict": attendance_dict,
        "attendance_grid": attendance_grid,
        "month_info": month_info,
        "day_range": day_range,
        "leave_quotas": leave_quotas,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_half_day": total_half_day,
        "total_late": total_late,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
    })


def teacher_list(request):
    teachers = Teacher.objects.select_related("school_class", "subject").all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)
    if filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
    if filter_status:
        teachers = teachers.filter(status=filter_status)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    teacher_names = Teacher.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST":
        if "delete_teacher" in request.POST:
            pk = request.POST.get("teacher_id")
            if pk:
                try:
                    teacher = get_object_or_404(Teacher, pk=pk)
                    teacher.delete()
                    messages.success(request, "Teacher deleted successfully.")
                except Exception:
                    messages.error(request, "Error deleting teacher.")
            else:
                messages.error(request, "No teacher ID provided.")
            return redirect("people:teacher-list")
        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("teacher_ids")
            if ids:
                Teacher.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} teacher(s) deleted successfully.")
            return redirect("people:teacher-list")

    return render(request, "portaluser/people/teachers.html", {
        "teachers": teachers,
        "class_names": class_names,
        "teacher_names": teacher_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_name": filter_name,
        "filter_class": filter_class,
        "filter_status": filter_status,
    })


def teacher_grid(request):
    teachers = Teacher.objects.select_related("school_class", "subject").all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    filter_gender = request.GET.get("filter_gender", "").strip()

    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)
    if filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
    if filter_status:
        teachers = teachers.filter(status=filter_status)
    if filter_gender:
        teachers = teachers.filter(gender=filter_gender)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST" and "delete_teacher" in request.POST:
        pk = request.POST.get("teacher_id")
        if pk:
            try:
                teacher = get_object_or_404(Teacher, pk=pk)
                teacher.delete()
                messages.success(request, "Teacher deleted successfully.")
            except Exception:
                messages.error(request, "Error deleting teacher.")
        else:
            messages.error(request, "No teacher ID provided.")
        return redirect("people:teacher-grid")

    return render(request, "portaluser/people/teacher-grid.html", {
        "teachers": teachers,
        "class_names": class_names,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_name": filter_name,
        "filter_class": filter_class,
        "filter_status": filter_status,
        "filter_gender": filter_gender,
    })


def teacher_details_redirect(request):
    teacher = Teacher.objects.first()
    if teacher:
        return redirect("people:teacher-details", pk=teacher.pk)
    return redirect("people:teacher-list")


def teacher_details(request, pk):
    teacher = get_object_or_404(
        Teacher.objects.select_related("school_class", "subject"),
        pk=pk,
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    languages = [lang.strip() for lang in teacher.languages_known.split(",") if lang.strip()]

    return render(request, "portaluser/people/teacher-details.html", {
        "teacher": teacher,
        "languages": languages,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
    })


def _parse_date(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def _generate_teacher_id():
    prefix = "T"
    last = Teacher.objects.order_by("-pk").first()
    next_num = (last.pk + 1) if last else 1
    return f"{prefix}{849127 - next_num + 1}"


def add_teacher(request):
    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    subjects = Subject.objects.filter(is_active=True).order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()
    next_teacher_id = _generate_teacher_id()

    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            if not name:
                first = request.POST.get("first_name", "").strip()
                last = request.POST.get("last_name", "").strip()
                name = " ".join(filter(None, [first, last]))
            if not name:
                messages.error(request, "Teacher name is required.")
                return render(request, "portaluser/people/add-teacher.html", {
                    "class_names": class_names,
                    "subjects": subjects,
                    "current_academic_year": current_academic_year,
                    "academic_years": academic_years,
                    "school_name": school.name if school else "Global International",
                    "next_teacher_id": next_teacher_id,
                })

            school_class = None
            class_name = request.POST.get("school_class", "")
            if class_name:
                school_class = SchoolClass.objects.filter(name=class_name).first()

            subject = None
            subject_id = request.POST.get("subject", "")
            if subject_id:
                subject = Subject.objects.filter(pk=subject_id).first()

            languages = request.POST.getlist("languages_known")
            languages_known = ", ".join(languages) if languages else request.POST.get("languages_known", "")

            teacher = Teacher(
                name=name,
                school_class=school_class,
                subject=subject,
                email=request.POST.get("email", ""),
                phone=request.POST.get("phone", ""),
                primary_contact_number=request.POST.get("primary_contact_number", ""),
                date_of_join=_parse_date(request.POST.get("date_of_join", "")),
                gender=request.POST.get("gender", "male"),
                date_of_birth=_parse_date(request.POST.get("date_of_birth", "")),
                status=request.POST.get("status", "active"),
                address=request.POST.get("address", ""),
                permanent_address=request.POST.get("permanent_address", ""),
                qualification=request.POST.get("qualification", ""),
                experience=request.POST.get("work_experience", "") or request.POST.get("experience", ""),
                # Personal Information
                blood_group=request.POST.get("blood_group", ""),
                marital_status=request.POST.get("marital_status", ""),
                languages_known=languages_known,
                father_name=request.POST.get("father_name", ""),
                mother_name=request.POST.get("mother_name", ""),
                pan_number=request.POST.get("pan_number", ""),
                notes=request.POST.get("notes", ""),
                # Previous School
                previous_school=request.POST.get("previous_school", ""),
                previous_school_address=request.POST.get("previous_school_address", ""),
                previous_school_phone=request.POST.get("previous_school_phone", ""),
                # Payroll
                epf_no=request.POST.get("epf_no", ""),
                basic_salary=request.POST.get("basic_salary", ""),
                contract_type=request.POST.get("contract_type", ""),
                work_shift=request.POST.get("work_shift", ""),
                work_location=request.POST.get("work_location", ""),
                date_of_leaving=_parse_date(request.POST.get("date_of_leaving", "")),
                # Leaves
                medical_leaves=request.POST.get("medical_leaves", ""),
                casual_leaves=request.POST.get("casual_leaves", ""),
                maternity_leaves=request.POST.get("maternity_leaves", ""),
                sick_leaves=request.POST.get("sick_leaves", ""),
                # Bank Details
                account_name=request.POST.get("account_name", ""),
                account_number=request.POST.get("account_number", ""),
                bank_name=request.POST.get("bank_name", ""),
                ifsc_code=request.POST.get("ifsc_code", ""),
                branch_name=request.POST.get("branch_name", ""),
                # Transport
                route=request.POST.get("route", ""),
                vehicle_number=request.POST.get("vehicle_number", ""),
                pickup_point=request.POST.get("pickup_point", ""),
                # Hostel
                hostel=request.POST.get("hostel", ""),
                room_no=request.POST.get("room_no", ""),
                # Social Media
                facebook=request.POST.get("facebook", ""),
                instagram=request.POST.get("instagram", ""),
                linkedin=request.POST.get("linkedin", ""),
                youtube=request.POST.get("youtube", ""),
                twitter=request.POST.get("twitter", ""),
            )

            if request.FILES.get("profile_image"):
                teacher.profile_image = request.FILES["profile_image"]
            if request.FILES.get("resume"):
                teacher.resume = request.FILES["resume"]
            if request.FILES.get("joining_letter"):
                teacher.joining_letter = request.FILES["joining_letter"]

            teacher.save()
            messages.success(request, f"Teacher {teacher.name} added successfully.")
            return redirect("people:teacher-list")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "portaluser/people/add-teacher.html", {
        "class_names": class_names,
        "subjects": subjects,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "next_teacher_id": next_teacher_id,
    })


def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    subjects = Subject.objects.filter(is_active=True).order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    name_parts = teacher.name.split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    languages_list = [lang.strip() for lang in teacher.languages_known.split(",") if lang.strip()]

    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            if not name:
                first = request.POST.get("first_name", "").strip()
                last = request.POST.get("last_name", "").strip()
                name = " ".join(filter(None, [first, last]))
            if not name:
                messages.error(request, "Teacher name is required.")
                return render(request, "portaluser/people/edit-teacher.html", {
                    "teacher": teacher,
                    "class_names": class_names,
                    "subjects": subjects,
                    "current_academic_year": current_academic_year,
                    "academic_years": academic_years,
                    "school_name": school.name if school else "Global International",
                    "languages_list": languages_list,
                    "first_name": first_name,
                    "last_name": last_name,
                })

            school_class = None
            class_name = request.POST.get("school_class", "")
            if class_name:
                school_class = SchoolClass.objects.filter(name=class_name).first()

            subject = None
            subject_id = request.POST.get("subject", "")
            if subject_id:
                subject = Subject.objects.filter(pk=subject_id).first()

            languages_raw = request.POST.get("languages_known", "")
            teacher.name = name
            teacher_id = request.POST.get("teacher_id", "").strip()
            if teacher_id:
                teacher.teacher_id = teacher_id
            teacher.school_class = school_class
            teacher.subject = subject
            teacher.email = request.POST.get("email", "")
            teacher.phone = request.POST.get("phone", "")
            teacher.primary_contact_number = request.POST.get("primary_contact_number", "")
            teacher.date_of_join = _parse_date(request.POST.get("date_of_join", ""))
            teacher.gender = request.POST.get("gender", "male")
            teacher.date_of_birth = _parse_date(request.POST.get("date_of_birth", ""))
            teacher.status = request.POST.get("status", "active")
            teacher.address = request.POST.get("address", "")
            teacher.permanent_address = request.POST.get("permanent_address", "")
            teacher.qualification = request.POST.get("qualification", "")
            teacher.experience = request.POST.get("work_experience", "") or request.POST.get("experience", "")
            teacher.blood_group = request.POST.get("blood_group", "")
            teacher.marital_status = request.POST.get("marital_status", "")
            teacher.languages_known = languages_raw
            teacher.father_name = request.POST.get("father_name", "")
            teacher.mother_name = request.POST.get("mother_name", "")
            teacher.pan_number = request.POST.get("pan_number", "")
            teacher.notes = request.POST.get("notes", "")
            teacher.previous_school = request.POST.get("previous_school", "")
            teacher.previous_school_address = request.POST.get("previous_school_address", "")
            teacher.previous_school_phone = request.POST.get("previous_school_phone", "")
            teacher.epf_no = request.POST.get("epf_no", "")
            teacher.basic_salary = request.POST.get("basic_salary", "")
            teacher.contract_type = request.POST.get("contract_type", "")
            teacher.work_shift = request.POST.get("work_shift", "")
            teacher.work_location = request.POST.get("work_location", "")
            teacher.date_of_leaving = _parse_date(request.POST.get("date_of_leaving", ""))
            teacher.medical_leaves = request.POST.get("medical_leaves", "")
            teacher.casual_leaves = request.POST.get("casual_leaves", "")
            teacher.maternity_leaves = request.POST.get("maternity_leaves", "")
            teacher.sick_leaves = request.POST.get("sick_leaves", "")
            teacher.account_name = request.POST.get("account_name", "")
            teacher.account_number = request.POST.get("account_number", "")
            teacher.bank_name = request.POST.get("bank_name", "")
            teacher.ifsc_code = request.POST.get("ifsc_code", "")
            teacher.branch_name = request.POST.get("branch_name", "")
            teacher.route = request.POST.get("route", "")
            teacher.vehicle_number = request.POST.get("vehicle_number", "")
            teacher.pickup_point = request.POST.get("pickup_point", "")
            teacher.hostel = request.POST.get("hostel", "")
            teacher.room_no = request.POST.get("room_no", "")
            teacher.facebook = request.POST.get("facebook", "")
            teacher.instagram = request.POST.get("instagram", "")
            teacher.linkedin = request.POST.get("linkedin", "")
            teacher.youtube = request.POST.get("youtube", "")
            teacher.twitter = request.POST.get("twitter", "")

            if request.FILES.get("profile_image"):
                teacher.profile_image = request.FILES["profile_image"]
            if request.FILES.get("resume"):
                teacher.resume = request.FILES["resume"]
            if request.FILES.get("joining_letter"):
                teacher.joining_letter = request.FILES["joining_letter"]

            teacher.save()
            messages.success(request, f"Teacher {teacher.name} updated successfully.")
            return redirect("people:teacher-list")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "portaluser/people/edit-teacher.html", {
        "teacher": teacher,
        "class_names": class_names,
        "subjects": subjects,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "languages_list": languages_list,
        "first_name": first_name,
        "last_name": last_name,
    })


def teacher_export_pdf(request):
    teachers = Teacher.objects.select_related("school_class", "subject").all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)
    if filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
    if filter_status:
        teachers = teachers.filter(status=filter_status)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/people/teacher-print.html", {
        "teachers": teachers,
        "school_name": school.name if school else "Global International",
        "filter_name": filter_name,
        "filter_class": filter_class,
        "filter_status": filter_status,
    })


def teacher_export_excel(request):
    teachers = Teacher.objects.select_related("school_class", "subject").all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)
    if filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
    if filter_status:
        teachers = teachers.filter(status=filter_status)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    filename = "teachers_list"
    if filter_class:
        filename += f"_{filter_class}"
    filename += f"_{date.today().strftime('%Y%m%d')}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Class", "Subject", "Email", "Phone", "Date of Join", "Status"])

    for teacher in teachers:
        writer.writerow([
            teacher.teacher_id,
            teacher.name,
            teacher.school_class.name if teacher.school_class else "-",
            teacher.subject.name if teacher.subject else "-",
            teacher.email or "-",
            teacher.phone or "-",
            teacher.date_of_join.strftime("%d %b %Y") if teacher.date_of_join else "-",
            teacher.status.capitalize(),
        ])

    return response


def staff_list(request):
    staff_members = Staff.objects.all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_department = request.GET.get("filter_department", "").strip()
    filter_designation = request.GET.get("filter_designation", "").strip()

    if filter_name:
        staff_members = staff_members.filter(name__icontains=filter_name)
    if filter_department:
        staff_members = staff_members.filter(department__icontains=filter_department)
    if filter_designation:
        staff_members = staff_members.filter(designation__icontains=filter_designation)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        staff_members = staff_members.order_by("-name")
    else:
        staff_members = staff_members.order_by("name")

    staff_names = Staff.objects.values_list("name", flat=True).distinct().order_by("name")
    departments = Staff.objects.values_list("department", flat=True).distinct().order_by("department")
    designations = Staff.objects.values_list("designation", flat=True).distinct().order_by("designation")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST":
        if "delete_staff" in request.POST:
            pk = request.POST.get("staff_id")
            if pk:
                try:
                    staff_member = get_object_or_404(Staff, pk=pk)
                    staff_member.delete()
                    messages.success(request, "Staff deleted successfully.")
                except Exception:
                    messages.error(request, "Error deleting staff.")
            else:
                messages.error(request, "No staff ID provided.")
            return redirect("people:staff-list")
        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("staff_ids")
            if ids:
                Staff.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} staff(s) deleted successfully.")
            return redirect("people:staff-list")

    return render(request, "portaluser/people/staffs.html", {
        "staff_members": staff_members,
        "staff_names": staff_names,
        "departments": departments,
        "designations": designations,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_name": filter_name,
        "filter_department": filter_department,
        "filter_designation": filter_designation,
    })


def staff_details_redirect(request):
    staff_member = Staff.objects.first()
    if staff_member:
        return redirect("people:staff-details", pk=staff_member.pk)
    return redirect("people:staff-list")


def staff_details(request, pk):
    staff_member = get_object_or_404(Staff, pk=pk)
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/people/staff-details.html", {
        "staff_member": staff_member,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
    })


def _generate_staff_id():
    prefix = "S"
    last = Staff.objects.order_by("-pk").first()
    next_num = (last.pk + 1) if last else 1
    return f"{prefix}{849127 - next_num + 1}"


def add_staff(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()
    next_staff_id = _generate_staff_id()

    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            if not name:
                first = request.POST.get("first_name", "").strip()
                last = request.POST.get("last_name", "").strip()
                name = " ".join(filter(None, [first, last]))
            if not name:
                messages.error(request, "Staff name is required.")
                return render(request, "portaluser/people/add-staff.html", {
                    "current_academic_year": current_academic_year,
                    "academic_years": academic_years,
                    "school_name": school.name if school else "Global International",
                    "next_staff_id": next_staff_id,
                })

            languages = request.POST.getlist("languages_known")
            languages_known = ", ".join(languages) if languages else request.POST.get("languages_known", "")

            staff_member = Staff(
                name=name,
                role=request.POST.get("role", ""),
                department=request.POST.get("department", ""),
                designation=request.POST.get("designation", ""),
                email=request.POST.get("email", ""),
                phone=request.POST.get("phone", ""),
                primary_contact_number=request.POST.get("primary_contact_number", ""),
                date_of_join=_parse_date(request.POST.get("date_of_join", "")),
                gender=request.POST.get("gender", "male"),
                date_of_birth=_parse_date(request.POST.get("date_of_birth", "")),
                status=request.POST.get("status", "active"),
                address=request.POST.get("address", ""),
                permanent_address=request.POST.get("permanent_address", ""),
                qualification=request.POST.get("qualification", ""),
                experience=request.POST.get("experience", ""),
                notes=request.POST.get("notes", ""),
                # Personal Information
                blood_group=request.POST.get("blood_group", ""),
                marital_status=request.POST.get("marital_status", ""),
                languages_known=languages_known,
                father_name=request.POST.get("father_name", ""),
                mother_name=request.POST.get("mother_name", ""),
                # Payroll
                epf_no=request.POST.get("epf_no", ""),
                basic_salary=request.POST.get("basic_salary", ""),
                contract_type=request.POST.get("contract_type", ""),
                work_shift=request.POST.get("work_shift", ""),
                work_location=request.POST.get("work_location", ""),
                # Leaves
                medical_leaves=request.POST.get("medical_leaves", ""),
                casual_leaves=request.POST.get("casual_leaves", ""),
                maternity_leaves=request.POST.get("maternity_leaves", ""),
                sick_leaves=request.POST.get("sick_leaves", ""),
                # Bank Details
                account_name=request.POST.get("account_name", ""),
                account_number=request.POST.get("account_number", ""),
                bank_name=request.POST.get("bank_name", ""),
                ifsc_code=request.POST.get("ifsc_code", ""),
                branch_name=request.POST.get("branch_name", ""),
                # Transport
                route=request.POST.get("route", ""),
                vehicle_number=request.POST.get("vehicle_number", ""),
                pickup_point=request.POST.get("pickup_point", ""),
                # Hostel
                hostel=request.POST.get("hostel", ""),
                room_no=request.POST.get("room_no", ""),
                # Social Media
                facebook=request.POST.get("facebook", ""),
                twitter=request.POST.get("twitter", ""),
                linkedin=request.POST.get("linkedin", ""),
                instagram=request.POST.get("instagram", ""),
            )

            if request.FILES.get("profile_image"):
                staff_member.profile_image = request.FILES["profile_image"]
            if request.FILES.get("resume"):
                staff_member.resume = request.FILES["resume"]
            if request.FILES.get("joining_letter"):
                staff_member.joining_letter = request.FILES["joining_letter"]

            staff_member.save()
            messages.success(request, f"Staff {staff_member.name} added successfully.")
            return redirect("people:staff-list")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "portaluser/people/add-staff.html", {
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "next_staff_id": next_staff_id,
    })


def edit_staff(request, pk):
    staff_member = get_object_or_404(Staff, pk=pk)
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    name_parts = staff_member.name.split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    languages = [lang.strip() for lang in staff_member.languages_known.split(",") if lang.strip()]

    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            if not name:
                first = request.POST.get("first_name", "").strip()
                last = request.POST.get("last_name", "").strip()
                name = " ".join(filter(None, [first, last]))
            if not name:
                messages.error(request, "Staff name is required.")
                return render(request, "portaluser/people/edit-staff.html", {
                    "staff_member": staff_member,
                    "current_academic_year": current_academic_year,
                    "academic_years": academic_years,
                    "school_name": school.name if school else "Global International",
                    "first_name": first_name,
                    "last_name": last_name,
                    "languages": languages,
                })

            languages = request.POST.getlist("languages_known")
            languages_known = ", ".join(languages) if languages else request.POST.get("languages_known", "")

            staff_member.name = name
            staff_member.role = request.POST.get("role", "")
            staff_member.department = request.POST.get("department", "")
            staff_member.designation = request.POST.get("designation", "")
            staff_member.email = request.POST.get("email", "")
            staff_member.phone = request.POST.get("phone", "")
            staff_member.primary_contact_number = request.POST.get("primary_contact_number", "")
            staff_member.date_of_join = _parse_date(request.POST.get("date_of_join", ""))
            staff_member.gender = request.POST.get("gender", "male")
            staff_member.date_of_birth = _parse_date(request.POST.get("date_of_birth", ""))
            staff_member.status = request.POST.get("status", "active")
            staff_member.address = request.POST.get("address", "")
            staff_member.permanent_address = request.POST.get("permanent_address", "")
            staff_member.qualification = request.POST.get("qualification", "")
            staff_member.experience = request.POST.get("experience", "")
            staff_member.notes = request.POST.get("notes", "")
            staff_member.blood_group = request.POST.get("blood_group", "")
            staff_member.marital_status = request.POST.get("marital_status", "")
            staff_member.languages_known = languages_known
            staff_member.father_name = request.POST.get("father_name", "")
            staff_member.mother_name = request.POST.get("mother_name", "")
            staff_member.epf_no = request.POST.get("epf_no", "")
            staff_member.basic_salary = request.POST.get("basic_salary", "")
            staff_member.contract_type = request.POST.get("contract_type", "")
            staff_member.work_shift = request.POST.get("work_shift", "")
            staff_member.work_location = request.POST.get("work_location", "")
            staff_member.medical_leaves = request.POST.get("medical_leaves", "")
            staff_member.casual_leaves = request.POST.get("casual_leaves", "")
            staff_member.maternity_leaves = request.POST.get("maternity_leaves", "")
            staff_member.sick_leaves = request.POST.get("sick_leaves", "")
            staff_member.account_name = request.POST.get("account_name", "")
            staff_member.account_number = request.POST.get("account_number", "")
            staff_member.bank_name = request.POST.get("bank_name", "")
            staff_member.ifsc_code = request.POST.get("ifsc_code", "")
            staff_member.branch_name = request.POST.get("branch_name", "")
            staff_member.route = request.POST.get("route", "")
            staff_member.vehicle_number = request.POST.get("vehicle_number", "")
            staff_member.pickup_point = request.POST.get("pickup_point", "")
            staff_member.hostel = request.POST.get("hostel", "")
            staff_member.room_no = request.POST.get("room_no", "")
            staff_member.facebook = request.POST.get("facebook", "")
            staff_member.twitter = request.POST.get("twitter", "")
            staff_member.linkedin = request.POST.get("linkedin", "")
            staff_member.instagram = request.POST.get("instagram", "")

            if request.FILES.get("profile_image"):
                staff_member.profile_image = request.FILES["profile_image"]
            if request.FILES.get("resume"):
                staff_member.resume = request.FILES["resume"]
            if request.FILES.get("joining_letter"):
                staff_member.joining_letter = request.FILES["joining_letter"]

            staff_member.save()
            messages.success(request, f"Staff {staff_member.name} updated successfully.")
            return redirect("people:staff-list")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "portaluser/people/edit-staff.html", {
        "staff_member": staff_member,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "first_name": first_name,
        "last_name": last_name,
        "languages": languages,
    })


def staff_export_pdf(request):
    staff_members = Staff.objects.all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_department = request.GET.get("filter_department", "").strip()
    filter_designation = request.GET.get("filter_designation", "").strip()

    if filter_name:
        staff_members = staff_members.filter(name__icontains=filter_name)
    if filter_department:
        staff_members = staff_members.filter(department__icontains=filter_department)
    if filter_designation:
        staff_members = staff_members.filter(designation__icontains=filter_designation)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        staff_members = staff_members.order_by("-name")
    else:
        staff_members = staff_members.order_by("name")

    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/people/staff-print.html", {
        "staff_members": staff_members,
        "school_name": school.name if school else "Global International",
        "filter_name": filter_name,
        "filter_department": filter_department,
        "filter_designation": filter_designation,
    })


def staff_export_excel(request):
    staff_members = Staff.objects.all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_department = request.GET.get("filter_department", "").strip()
    filter_designation = request.GET.get("filter_designation", "").strip()

    if filter_name:
        staff_members = staff_members.filter(name__icontains=filter_name)
    if filter_department:
        staff_members = staff_members.filter(department__icontains=filter_department)
    if filter_designation:
        staff_members = staff_members.filter(designation__icontains=filter_designation)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        staff_members = staff_members.order_by("-name")
    else:
        staff_members = staff_members.order_by("name")

    filename = "staff_list"
    if filter_department:
        filename += f"_{filter_department}"
    filename += f"_{date.today().strftime('%Y%m%d')}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Department", "Designation", "Phone", "Email", "Date of Join"])

    for staff_member in staff_members:
        writer.writerow([
            staff_member.staff_id,
            staff_member.name,
            staff_member.department or "-",
            staff_member.designation or "-",
            staff_member.phone or "-",
            staff_member.email or "-",
            staff_member.date_of_join.strftime("%d %b %Y") if staff_member.date_of_join else "-",
        ])

    return response


def get_sections(request):
    class_name = request.GET.get("class_name", "")
    sections = []
    if class_name:
        school_class = SchoolClass.objects.filter(name=class_name).first()
        if school_class:
            sections = list(
                Section.objects.filter(school_class=school_class).values("name", "pk")
            )
    return JsonResponse(sections, safe=False)


@require_POST
def add_student_ajax(request):
    try:
        name = " ".join(filter(None, [request.POST.get("first_name", ""), request.POST.get("last_name", "")]))
        if not name:
            return JsonResponse({"success": False, "error": "Name is required."}, status=400)

        school_class = get_object_or_404(SchoolClass, name=request.POST.get("school_class"))
        section = get_object_or_404(Section, school_class=school_class, name=request.POST.get("section"))
        academic_year = AcademicYear.objects.filter(is_current=True).first()

        dob_str = request.POST.get("date_of_birth", "")
        date_of_birth = None
        if dob_str:
            try:
                date_of_birth = datetime.strptime(dob_str, "%d %b %Y").date()
            except ValueError:
                pass

        student = Student(
            admission_no=request.POST.get("admission_no", ""),
            roll_no=request.POST.get("roll_no", ""),
            name=name,
            school_class=school_class,
            section=section,
            gender=request.POST.get("gender", "male"),
            date_of_birth=date_of_birth,
            status=request.POST.get("status", "active"),
            academic_year=academic_year,
        )

        if request.FILES.get("profile_image"):
            student.profile_image = request.FILES["profile_image"]

        student.save()
        student.refresh_from_db()

        return JsonResponse({
            "success": True,
            "student": {
                "pk": student.pk,
                "admission_no": student.admission_no,
                "name": student.name,
                "class": student.school_class.name,
                "section": student.section.name,
                "roll_no": student.roll_no,
                "gender": student.get_gender_display(),
                "status": student.status,
                "joined_on": student.created_at.strftime("%d %b %Y"),
                "profile_image": student.profile_image.url if student.profile_image else None,
            },
        })
    except Http404:
        return JsonResponse({"success": False, "error": "Selected class or section not found."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def student_attendance_list(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    students = Student.objects.select_related("school_class", "section").filter(status="active")

    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(section__name=filter_section)

    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")

    attendance_statuses = StudentAttendance.ATTENDANCE_STATUS_CHOICES

    attendance_records = StudentAttendance.objects.filter(date=attendance_date, student__in=students)
    attendance_status_dict = {}
    attendance_remarks_dict = {}
    for rec in attendance_records:
        attendance_status_dict[rec.student_id] = rec.status
        attendance_remarks_dict[rec.student_id] = rec.remarks

    if request.method == "POST":
        if "mark_attendance" in request.POST:
            for student in students:
                status_key = f"status_{student.pk}"
                remarks_key = f"remarks_{student.pk}"
                att_status = request.POST.get(status_key, "").strip()
                att_remarks = request.POST.get(remarks_key, "").strip()
                if att_status in dict(attendance_statuses):
                    StudentAttendance.objects.update_or_create(
                        student=student,
                        date=attendance_date,
                        defaults={
                            "status": att_status,
                            "remarks": att_remarks,
                            "academic_year": current_academic_year,
                        },
                    )
            messages.success(request, f"Attendance for {attendance_date.strftime('%d %b %Y')} saved successfully.")
            return redirect(request.path + "?" + request.GET.urlencode() if request.GET else request.path)

        elif "bulk_delete" in request.POST:
            student_ids = request.POST.getlist("selected_items")
            if student_ids:
                deleted = StudentAttendance.objects.filter(student__pk__in=student_ids, date=attendance_date).delete()
                messages.success(request, "Selected attendance records deleted.")
            return redirect(request.path + "?" + request.GET.urlencode() if request.GET else request.path)

    return render(request, "portaluser/people/student-attendance.html", {
        "students": students,
        "class_names": class_names,
        "section_names": section_names,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_date": filter_date,
        "attendance_date": attendance_date,
        "attendance_status_dict": attendance_status_dict,
        "attendance_remarks_dict": attendance_remarks_dict,
        "attendance_statuses": attendance_statuses,
        "sort": sort,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


@require_POST
def student_attendance_save_ajax(request):
    today = date.today()
    student_id = request.POST.get("student_id")
    attendance_date_str = request.POST.get("attendance_date", today.strftime("%Y-%m-%d")).strip()
    status_val = request.POST.get("status", "").strip()
    remarks_val = request.POST.get("remarks", "").strip()

    try:
        attendance_date = datetime.strptime(attendance_date_str, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = today

    valid_statuses = dict(StudentAttendance.ATTENDANCE_STATUS_CHOICES)
    if status_val not in valid_statuses:
        return JsonResponse({"success": False, "error": f"Invalid status: {status_val}"}, status=400)

    if not student_id:
        return JsonResponse({"success": False, "error": "student_id is required."}, status=400)

    try:
        student = Student.objects.get(pk=student_id, status="active")
    except Student.DoesNotExist:
        return JsonResponse({"success": False, "error": "Student not found."}, status=404)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    rec, created = StudentAttendance.objects.update_or_create(
        student=student,
        date=attendance_date,
        defaults={
            "status": status_val,
            "remarks": remarks_val,
            "academic_year": current_academic_year,
        },
    )

    return JsonResponse({
        "success": True,
        "student_id": student.pk,
        "status": rec.status,
        "remarks": rec.remarks,
        "saved": "new" if created else "updated",
        "date": rec.date.strftime("%d %b %Y"),
    })


def student_attendance_export_pdf(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    student_id = request.GET.get("student_id", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    title = "Student Attendance"
    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    students = Student.objects.select_related("school_class", "section").filter(status="active")

    if student_id:
        students = students.filter(pk=student_id)
        student_obj = students.first()
        if student_obj:
            title = f"{student_obj.name} - Attendance"
    elif filter_class:
        students = students.filter(school_class__name=filter_class)
        title += f" - {filter_class}"
    if filter_section:
        students = students.filter(section__name=filter_section)
        title += f" - Section {filter_section}"

    title += f" ({attendance_date.strftime('%d %b %Y')})"

    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    attendance_records = StudentAttendance.objects.filter(date=attendance_date, student__in=students)
    attendance_data = {}
    remarks_data = {}
    for rec in attendance_records:
        attendance_data[rec.student_id] = rec.status
        remarks_data[rec.student_id] = rec.remarks

    context = {
        "title": title,
        "students": students,
        "attendance_data": attendance_data,
        "remarks_data": remarks_data,
        "attendance_statuses": StudentAttendance.ATTENDANCE_STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "filter_date": filter_date,
    }
    return render(request, "portaluser/people/student-attendance-print.html", context)


def student_attendance_export_excel(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    student_id = request.GET.get("student_id", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    filename = "student_attendance"
    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    if student_id:
        filename += f"_student_{student_id}"
    elif filter_class:
        filename += f"_{filter_class}"
    if filter_section:
        filename += f"_{filter_section}"
    filename += f"_{attendance_date.strftime('%Y%m%d')}"
    filename = filename.replace(" ", "_")

    students = Student.objects.select_related("school_class", "section").filter(status="active")

    if student_id:
        students = students.filter(pk=student_id)
    elif filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(section__name=filter_section)

    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    attendance_records = StudentAttendance.objects.filter(date=attendance_date, student__in=students)
    attendance_data = {}
    remarks_data = {}
    for rec in attendance_records:
        attendance_data[rec.student_id] = rec.status
        remarks_data[rec.student_id] = rec.remarks

    status_display = dict(StudentAttendance.ATTENDANCE_STATUS_CHOICES)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["Admission No", "Roll No", "Student Name", "Class", "Section", "Attendance Status", "Remarks"])

    for student in students:
        status_key = attendance_data.get(student.pk, "")
        status_display_val = status_display.get(status_key, "-")
        if status_display_val == "-" and status_key:
            status_display_val = status_key
        writer.writerow([
            student.admission_no,
            student.roll_no or "-",
            student.name,
            student.school_class.name,
            student.section.name,
            status_display_val,
            remarks_data.get(student.pk, ""),
        ])

    return response


def teacher_attendance_list(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    filter_id = request.GET.get("filter_id", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    teachers = Teacher.objects.select_related("school_class", "subject").filter(status="active")

    if filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)
    if filter_id:
        teachers = teachers.filter(teacher_id=filter_id)

    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    teacher_names = Teacher.objects.values_list("name", flat=True).distinct().order_by("name")

    attendance_statuses = TeacherAttendance.ATTENDANCE_STATUS_CHOICES

    attendance_records = TeacherAttendance.objects.filter(date=attendance_date, teacher__in=teachers)
    attendance_status_dict = {}
    attendance_remarks_dict = {}
    for rec in attendance_records:
        attendance_status_dict[rec.teacher_id] = rec.status
        attendance_remarks_dict[rec.teacher_id] = rec.remarks

    if request.method == "POST":
        if "mark_attendance" in request.POST:
            for teacher in teachers:
                status_key = f"status_{teacher.pk}"
                remarks_key = f"remarks_{teacher.pk}"
                att_status = request.POST.get(status_key, "").strip()
                att_remarks = request.POST.get(remarks_key, "").strip()
                if att_status in dict(attendance_statuses):
                    TeacherAttendance.objects.update_or_create(
                        teacher=teacher,
                        date=attendance_date,
                        defaults={
                            "status": att_status,
                            "remarks": att_remarks,
                            "academic_year": current_academic_year,
                        },
                    )
            messages.success(request, f"Attendance for {attendance_date.strftime('%d %b %Y')} saved successfully.")
            return redirect(request.path + "?" + request.GET.urlencode() if request.GET else request.path)

        elif "bulk_delete" in request.POST:
            teacher_ids = request.POST.getlist("selected_items")
            if teacher_ids:
                TeacherAttendance.objects.filter(teacher__pk__in=teacher_ids, date=attendance_date).delete()
                messages.success(request, "Selected attendance records deleted.")
            return redirect(request.path + "?" + request.GET.urlencode() if request.GET else request.path)

    return render(request, "portaluser/people/teacher-attendance.html", {
        "teachers": teachers,
        "class_names": class_names,
        "teacher_names": teacher_names,
        "filter_class": filter_class,
        "filter_name": filter_name,
        "filter_status": filter_status,
        "filter_id": filter_id,
        "filter_date": filter_date,
        "attendance_date": attendance_date,
        "attendance_status_dict": attendance_status_dict,
        "attendance_remarks_dict": attendance_remarks_dict,
        "attendance_statuses": attendance_statuses,
        "sort": sort,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


@require_POST
def teacher_attendance_save_ajax(request):
    today = date.today()
    teacher_id = request.POST.get("teacher_id")
    attendance_date_str = request.POST.get("attendance_date", today.strftime("%Y-%m-%d")).strip()
    status_val = request.POST.get("status", "").strip()
    remarks_val = request.POST.get("remarks", "").strip()

    try:
        attendance_date = datetime.strptime(attendance_date_str, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = today

    valid_statuses = dict(TeacherAttendance.ATTENDANCE_STATUS_CHOICES)
    if status_val not in valid_statuses:
        return JsonResponse({"success": False, "error": f"Invalid status: {status_val}"}, status=400)

    if not teacher_id:
        return JsonResponse({"success": False, "error": "teacher_id is required."}, status=400)

    try:
        teacher = Teacher.objects.get(pk=teacher_id, status="active")
    except Teacher.DoesNotExist:
        return JsonResponse({"success": False, "error": "Teacher not found."}, status=404)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    rec, created = TeacherAttendance.objects.update_or_create(
        teacher=teacher,
        date=attendance_date,
        defaults={
            "status": status_val,
            "remarks": remarks_val,
            "academic_year": current_academic_year,
        },
    )

    return JsonResponse({
        "success": True,
        "teacher_id": teacher.pk,
        "status": rec.status,
        "remarks": rec.remarks,
        "saved": "new" if created else "updated",
        "date": rec.date.strftime("%d %b %Y"),
    })


def teacher_attendance_export_pdf(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    teacher_id = request.GET.get("teacher_id", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    title = "Teacher Attendance"
    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    teachers = Teacher.objects.select_related("school_class", "subject").filter(status="active")

    if teacher_id:
        teachers = teachers.filter(pk=teacher_id)
        teacher_obj = teachers.first()
        if teacher_obj:
            title = f"{teacher_obj.name} - Attendance"
    elif filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
        title += f" - {filter_class}"
    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)

    title += f" ({attendance_date.strftime('%d %b %Y')})"

    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    attendance_records = TeacherAttendance.objects.filter(date=attendance_date, teacher__in=teachers)
    attendance_data = {}
    remarks_data = {}
    for rec in attendance_records:
        attendance_data[rec.teacher_id] = rec.status
        remarks_data[rec.teacher_id] = rec.remarks

    context = {
        "title": title,
        "teachers": teachers,
        "attendance_data": attendance_data,
        "remarks_data": remarks_data,
        "attendance_statuses": TeacherAttendance.ATTENDANCE_STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "filter_date": filter_date,
    }
    return render(request, "portaluser/people/teacher-attendance-print.html", context)


def teacher_attendance_export_excel(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    teacher_id = request.GET.get("teacher_id", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    filename = "teacher_attendance"
    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    if teacher_id:
        filename += f"_teacher_{teacher_id}"
    elif filter_class:
        filename += f"_{filter_class}"
    if filter_name:
        filename += f"_{filter_name}"
    filename += f"_{attendance_date.strftime('%Y%m%d')}"
    filename = filename.replace(" ", "_")

    teachers = Teacher.objects.select_related("school_class", "subject").filter(status="active")

    if teacher_id:
        teachers = teachers.filter(pk=teacher_id)
    elif filter_class:
        teachers = teachers.filter(school_class__name=filter_class)
    if filter_name:
        teachers = teachers.filter(name__icontains=filter_name)

    if sort == "desc":
        teachers = teachers.order_by("-name")
    else:
        teachers = teachers.order_by("name")

    attendance_records = TeacherAttendance.objects.filter(date=attendance_date, teacher__in=teachers)
    attendance_data = {}
    remarks_data = {}
    for rec in attendance_records:
        attendance_data[rec.teacher_id] = rec.status
        remarks_data[rec.teacher_id] = rec.remarks

    status_display = dict(TeacherAttendance.ATTENDANCE_STATUS_CHOICES)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Teacher Name", "Class", "Attendance Status", "Remarks"])

    for teacher in teachers:
        status_key = attendance_data.get(teacher.pk, "")
        status_display_val = status_display.get(status_key, "-")
        if status_display_val == "-" and status_key:
            status_display_val = status_key
        writer.writerow([
            teacher.teacher_id,
            teacher.name,
            teacher.school_class.name if teacher.school_class else "-",
            status_display_val,
            remarks_data.get(teacher.pk, ""),
        ])

    return response


def parent_list(request):
    students = Student.objects.select_related("school_class", "section", "academic_year").all()

    filter_parent = request.GET.get("filter_parent", "").strip()
    filter_child = request.GET.get("filter_child", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort = request.GET.get("sort", "asc")

    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_child:
        students = students.filter(name__icontains=filter_child)

    parents_data = []
    for student in students:
        if student.father_name:
            parents_data.append({
                "parent_type": "father",
                "parent_name": student.father_name,
                "parent_email": student.father_email,
                "parent_phone": student.father_phone,
                "parent_image": student.father_image,
                "student": student,
            })
        if student.mother_name:
            parents_data.append({
                "parent_type": "mother",
                "parent_name": student.mother_name,
                "parent_email": student.mother_email,
                "parent_phone": student.mother_phone,
                "parent_image": student.mother_image,
                "student": student,
            })

    if filter_parent:
        parents_data = [p for p in parents_data if filter_parent.lower() in p["parent_name"].lower()]

    parent_groups = {}
    for entry in parents_data:
        key = (entry["parent_name"].strip().lower(), entry["parent_email"].strip().lower())
        if key not in parent_groups:
            parent_groups[key] = {
                "parent_name": entry["parent_name"],
                "parent_email": entry["parent_email"],
                "parent_phone": entry["parent_phone"],
                "parent_image": entry["parent_image"],
                "children": [],
            }
        parent_groups[key]["children"].append(entry["student"])
        if entry["parent_phone"] and not parent_groups[key]["parent_phone"]:
            parent_groups[key]["parent_phone"] = entry["parent_phone"]
        if entry["parent_image"] and not parent_groups[key]["parent_image"]:
            parent_groups[key]["parent_image"] = entry["parent_image"]

    parent_list_data = []
    seen_parent_names = set()
    for key, group in parent_groups.items():
        group["children"] = list(set(group["children"]))
        group["children"].sort(key=lambda s: s.name)
        parent_id_num = len(parent_list_data) + 1
        parent_id = f"P{124556 - parent_id_num + 1}"
        parent_list_data.append({
            "parent_id": parent_id,
            "parent_name": group["parent_name"],
            "parent_email": group["parent_email"] or "-",
            "parent_phone": group["parent_phone"] or "-",
            "parent_image": group["parent_image"],
            "children": group["children"],
            "first_child": group["children"][0] if group["children"] else None,
        })
        seen_parent_names.add(group["parent_name"].strip().lower())

    if sort == "desc":
        parent_list_data.sort(key=lambda p: p["parent_name"].lower(), reverse=True)
    else:
        parent_list_data.sort(key=lambda p: p["parent_name"].lower())

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    child_names = Student.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST":
        if "delete_parent" in request.POST:
            parent_name = request.POST.get("parent_name", "").strip()
            if parent_name:
                updated = Student.objects.filter(father_name=parent_name).update(father_name="", father_email="", father_phone="")
                updated += Student.objects.filter(mother_name=parent_name).update(mother_name="", mother_email="", mother_phone="")
                if updated:
                    messages.success(request, f"Parent '{parent_name}' deleted successfully.")
                else:
                    messages.error(request, "Parent not found.")
            return redirect("people:parent-list")

        if "add_parent" in request.POST:
            name = request.POST.get("parent_name", "").strip()
            phone = request.POST.get("parent_phone", "").strip()
            email = request.POST.get("parent_email", "").strip()
            child_ids = request.POST.getlist("child_ids")
            if name and child_ids:
                updated = 0
                for cid in child_ids:
                    try:
                        student = Student.objects.get(pk=cid)
                        if student.father_name and student.mother_name:
                            if not student.father_email and email:
                                student.father_email = email
                            if not student.father_phone and phone:
                                student.father_phone = phone
                        elif not student.father_name:
                            student.father_name = name
                            student.father_email = email
                            student.father_phone = phone
                        else:
                            student.mother_name = name
                            student.mother_email = email
                            student.mother_phone = phone
                        student.save()
                        updated += 1
                    except Student.DoesNotExist:
                        pass
                if updated:
                    messages.success(request, f"Parent '{name}' added to {updated} student(s).")
            return redirect("people:parent-list")

        if "edit_parent" in request.POST:
            old_name = request.POST.get("old_parent_name", "").strip()
            name = request.POST.get("parent_name", "").strip()
            phone = request.POST.get("parent_phone", "").strip()
            email = request.POST.get("parent_email", "").strip()
            child_ids = request.POST.getlist("child_ids")
            if old_name and name:
                for student in Student.objects.filter(father_name=old_name):
                    student.father_name = name
                    if email: student.father_email = email
                    if phone: student.father_phone = phone
                    student.save()
                for student in Student.objects.filter(mother_name=old_name):
                    student.mother_name = name
                    if email: student.mother_email = email
                    if phone: student.mother_phone = phone
                    student.save()
                messages.success(request, f"Parent '{old_name}' updated successfully.")
            return redirect("people:parent-list")

    parent_list_json = []
    for p in parent_list_data:
        children_json = []
        for c in p["children"]:
            children_json.append({
                "pk": c.pk,
                "name": c.name,
                "admission_no": c.admission_no,
                "roll_no": c.roll_no,
                "class_name": c.school_class.name if c.school_class else "-",
                "section_name": c.section.name if c.section else "-",
                "gender": c.get_gender_display(),
                "admission_date": c.admission_date.strftime("%d %b %Y") if c.admission_date else "-",
                "created_at": c.created_at.strftime("%d %b %Y") if c.created_at else "",
            })
        parent_list_json.append({
            "parent_name": p["parent_name"],
            "parent_email": p["parent_email"],
            "parent_phone": p["parent_phone"],
            "children": children_json,
        })

    return render(request, "portaluser/people/parents.html", {
        "parent_list": parent_list_data,
        "parent_list_json": json.dumps(parent_list_json),
        "class_names": class_names,
        "child_names": child_names,
        "students": students,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_parent": filter_parent,
        "filter_child": filter_child,
        "filter_class": filter_class,
        "filter_status": filter_status,
    })


def guardian_list(request):
    students = Student.objects.select_related("school_class", "section", "academic_year").all()

    filter_guardian = request.GET.get("filter_guardian", "").strip()
    filter_child = request.GET.get("filter_child", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort = request.GET.get("sort", "asc")

    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_child:
        students = students.filter(name__icontains=filter_child)

    guardians_data = []
    for student in students:
        if student.guardian_name:
            guardians_data.append({
                "guardian_name": student.guardian_name,
                "guardian_email": student.guardian_email or "",
                "guardian_phone": student.guardian_phone or "",
                "guardian_image": student.guardian_image,
                "guardian_relation": student.guardian_relation or "",
                "student": student,
            })

    if filter_guardian:
        guardians_data = [g for g in guardians_data if filter_guardian.lower() in g["guardian_name"].lower()]

    guardian_groups = {}
    for entry in guardians_data:
        key = (entry["guardian_name"].strip().lower(), entry["guardian_email"].strip().lower())
        if key not in guardian_groups:
            guardian_groups[key] = {
                "guardian_name": entry["guardian_name"],
                "guardian_email": entry["guardian_email"],
                "guardian_phone": entry["guardian_phone"],
                "guardian_image": entry["guardian_image"],
                "guardian_relation": entry["guardian_relation"],
                "children": [],
            }
        guardian_groups[key]["children"].append(entry["student"])
        if entry["guardian_phone"] and not guardian_groups[key]["guardian_phone"]:
            guardian_groups[key]["guardian_phone"] = entry["guardian_phone"]
        if entry["guardian_image"] and not guardian_groups[key]["guardian_image"]:
            guardian_groups[key]["guardian_image"] = entry["guardian_image"]

    guardian_list_data = []
    for key, group in guardian_groups.items():
        group["children"] = list(set(group["children"]))
        group["children"].sort(key=lambda s: s.name)
        guardian_id_num = len(guardian_list_data) + 1
        guardian_id = f"G{153735 - guardian_id_num + 1}"
        guardian_list_data.append({
            "guardian_id": guardian_id,
            "guardian_name": group["guardian_name"],
            "guardian_email": group["guardian_email"] or "-",
            "guardian_phone": group["guardian_phone"] or "-",
            "guardian_image": group["guardian_image"],
            "guardian_relation": group["guardian_relation"],
            "children": group["children"],
            "first_child": group["children"][0] if group["children"] else None,
        })

    if sort == "desc":
        guardian_list_data.sort(key=lambda g: g["guardian_name"].lower(), reverse=True)
    else:
        guardian_list_data.sort(key=lambda g: g["guardian_name"].lower())

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    child_names = Student.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    if request.method == "POST":
        if "delete_guardian" in request.POST:
            guardian_name = request.POST.get("guardian_name", "").strip()
            if guardian_name:
                updated = Student.objects.filter(guardian_name=guardian_name).update(
                    guardian_name="", guardian_email="", guardian_phone="",
                    guardian_relation="", guardian_address="", guardian_occupation=""
                )
                if updated:
                    messages.success(request, f"Guardian '{guardian_name}' deleted successfully.")
                else:
                    messages.error(request, "Guardian not found.")
            return redirect("people:guardian-list")

        if "add_guardian" in request.POST:
            name = request.POST.get("guardian_name", "").strip()
            phone = request.POST.get("guardian_phone", "").strip()
            email = request.POST.get("guardian_email", "").strip()
            relation = request.POST.get("guardian_relation", "").strip()
            child_ids = request.POST.getlist("child_ids")
            if name and child_ids:
                updated = 0
                for cid in child_ids:
                    try:
                        student = Student.objects.get(pk=cid)
                        student.guardian_name = name
                        student.guardian_email = email
                        student.guardian_phone = phone
                        student.guardian_relation = relation
                        student.save()
                        updated += 1
                    except Student.DoesNotExist:
                        pass
                if updated:
                    messages.success(request, f"Guardian '{name}' added to {updated} student(s).")
            return redirect("people:guardian-list")

        if "edit_guardian" in request.POST:
            old_name = request.POST.get("old_guardian_name", "").strip()
            name = request.POST.get("guardian_name", "").strip()
            phone = request.POST.get("guardian_phone", "").strip()
            email = request.POST.get("guardian_email", "").strip()
            relation = request.POST.get("guardian_relation", "").strip()
            child_ids = request.POST.getlist("child_ids")
            if old_name and name:
                for student in Student.objects.filter(guardian_name=old_name):
                    student.guardian_name = name
                    if email: student.guardian_email = email
                    if phone: student.guardian_phone = phone
                    if relation: student.guardian_relation = relation
                    student.save()
                messages.success(request, f"Guardian '{old_name}' updated successfully.")
            return redirect("people:guardian-list")

    guardian_list_json = []
    for g in guardian_list_data:
        children_json = []
        for c in g["children"]:
            children_json.append({
                "pk": c.pk,
                "name": c.name,
                "admission_no": c.admission_no,
                "roll_no": c.roll_no,
                "class_name": c.school_class.name if c.school_class else "-",
                "section_name": c.section.name if c.section else "-",
                "gender": c.get_gender_display(),
                "admission_date": c.admission_date.strftime("%d %b %Y") if c.admission_date else "-",
                "created_at": c.created_at.strftime("%d %b %Y") if c.created_at else "",
            })
        guardian_list_json.append({
            "guardian_name": g["guardian_name"],
            "guardian_email": g["guardian_email"],
            "guardian_phone": g["guardian_phone"],
            "guardian_relation": g["guardian_relation"],
            "children": children_json,
        })

    return render(request, "portaluser/people/guardians.html", {
        "guardian_list": guardian_list_data,
        "guardian_list_json": json.dumps(guardian_list_json),
        "class_names": class_names,
        "child_names": child_names,
        "students": students,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_guardian": filter_guardian,
        "filter_child": filter_child,
        "filter_class": filter_class,
        "filter_status": filter_status,
    })


def staff_attendance_list(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    filter_department = request.GET.get("filter_department", "").strip()
    filter_designation = request.GET.get("filter_designation", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_id = request.GET.get("filter_id", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    staff_members = Staff.objects.filter(status="active")

    if filter_department:
        staff_members = staff_members.filter(department__icontains=filter_department)
    if filter_designation:
        staff_members = staff_members.filter(designation__icontains=filter_designation)
    if filter_name:
        staff_members = staff_members.filter(name__icontains=filter_name)
    if filter_id:
        staff_members = staff_members.filter(staff_id=filter_id)

    if sort == "desc":
        staff_members = staff_members.order_by("-name")
    else:
        staff_members = staff_members.order_by("name")

    staff_names = Staff.objects.values_list("name", flat=True).distinct().order_by("name")
    departments = Staff.objects.values_list("department", flat=True).distinct().order_by("department")
    designations = Staff.objects.values_list("designation", flat=True).distinct().order_by("designation")

    attendance_statuses = StaffAttendance.ATTENDANCE_STATUS_CHOICES

    attendance_records = StaffAttendance.objects.filter(date=attendance_date, staff__in=staff_members)
    attendance_status_dict = {}
    attendance_remarks_dict = {}
    for rec in attendance_records:
        attendance_status_dict[rec.staff_id] = rec.status
        attendance_remarks_dict[rec.staff_id] = rec.remarks

    if request.method == "POST":
        if "mark_attendance" in request.POST:
            for staff_member in staff_members:
                status_key = f"status_{staff_member.pk}"
                remarks_key = f"remarks_{staff_member.pk}"
                att_status = request.POST.get(status_key, "").strip()
                att_remarks = request.POST.get(remarks_key, "").strip()
                if att_status in dict(attendance_statuses):
                    StaffAttendance.objects.update_or_create(
                        staff=staff_member,
                        date=attendance_date,
                        defaults={
                            "status": att_status,
                            "remarks": att_remarks,
                            "academic_year": current_academic_year,
                        },
                    )
            messages.success(request, f"Attendance for {attendance_date.strftime('%d %b %Y')} saved successfully.")
            return redirect(request.path + "?" + request.GET.urlencode() if request.GET else request.path)

        elif "bulk_delete" in request.POST:
            staff_ids = request.POST.getlist("selected_items")
            if staff_ids:
                StaffAttendance.objects.filter(staff__pk__in=staff_ids, date=attendance_date).delete()
                messages.success(request, "Selected attendance records deleted.")
            return redirect(request.path + "?" + request.GET.urlencode() if request.GET else request.path)

    return render(request, "portaluser/people/staff-attendance.html", {
        "staff_members": staff_members,
        "staff_names": staff_names,
        "departments": departments,
        "designations": designations,
        "filter_department": filter_department,
        "filter_designation": filter_designation,
        "filter_name": filter_name,
        "filter_id": filter_id,
        "filter_date": filter_date,
        "attendance_date": attendance_date,
        "attendance_status_dict": attendance_status_dict,
        "attendance_remarks_dict": attendance_remarks_dict,
        "attendance_statuses": attendance_statuses,
        "sort": sort,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


@require_POST
def staff_attendance_save_ajax(request):
    today = date.today()
    staff_id = request.POST.get("staff_id")
    attendance_date_str = request.POST.get("attendance_date", today.strftime("%Y-%m-%d")).strip()
    status_val = request.POST.get("status", "").strip()
    remarks_val = request.POST.get("remarks", "").strip()

    try:
        attendance_date = datetime.strptime(attendance_date_str, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = today

    valid_statuses = dict(StaffAttendance.ATTENDANCE_STATUS_CHOICES)
    if status_val not in valid_statuses:
        return JsonResponse({"success": False, "error": f"Invalid status: {status_val}"}, status=400)

    if not staff_id:
        return JsonResponse({"success": False, "error": "staff_id is required."}, status=400)

    try:
        staff_member = Staff.objects.get(pk=staff_id, status="active")
    except Staff.DoesNotExist:
        return JsonResponse({"success": False, "error": "Staff not found."}, status=404)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    rec, created = StaffAttendance.objects.update_or_create(
        staff=staff_member,
        date=attendance_date,
        defaults={
            "status": status_val,
            "remarks": remarks_val,
            "academic_year": current_academic_year,
        },
    )

    return JsonResponse({
        "success": True,
        "staff_id": staff_member.pk,
        "status": rec.status,
        "remarks": rec.remarks,
        "saved": "new" if created else "updated",
        "date": rec.date.strftime("%d %b %Y"),
    })


def staff_attendance_export_pdf(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    staff_id = request.GET.get("staff_id", "").strip()
    filter_department = request.GET.get("filter_department", "").strip()
    filter_designation = request.GET.get("filter_designation", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    title = "Staff Attendance"
    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    staff_members = Staff.objects.filter(status="active")

    if staff_id:
        staff_members = staff_members.filter(pk=staff_id)
        staff_obj = staff_members.first()
        if staff_obj:
            title = f"{staff_obj.name} - Attendance"
    elif filter_department:
        staff_members = staff_members.filter(department__icontains=filter_department)
        title += f" - {filter_department}"
    if filter_designation:
        staff_members = staff_members.filter(designation__icontains=filter_designation)
    if filter_name:
        staff_members = staff_members.filter(name__icontains=filter_name)

    title += f" ({attendance_date.strftime('%d %b %Y')})"

    if sort == "desc":
        staff_members = staff_members.order_by("-name")
    else:
        staff_members = staff_members.order_by("name")

    attendance_records = StaffAttendance.objects.filter(date=attendance_date, staff__in=staff_members)
    attendance_data = {}
    remarks_data = {}
    for rec in attendance_records:
        attendance_data[rec.staff_id] = rec.status
        remarks_data[rec.staff_id] = rec.remarks

    context = {
        "title": title,
        "staff_members": staff_members,
        "attendance_data": attendance_data,
        "remarks_data": remarks_data,
        "attendance_statuses": StaffAttendance.ATTENDANCE_STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "filter_date": filter_date,
    }
    return render(request, "portaluser/people/staff-attendance-print.html", context)


def staff_attendance_export_excel(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    staff_id = request.GET.get("staff_id", "").strip()
    filter_department = request.GET.get("filter_department", "").strip()
    filter_designation = request.GET.get("filter_designation", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_date = request.GET.get("filter_date", date.today().strftime("%Y-%m-%d")).strip()
    sort = request.GET.get("sort", "asc")

    filename = "staff_attendance"
    try:
        attendance_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
    except ValueError:
        attendance_date = date.today()

    if staff_id:
        filename += f"_staff_{staff_id}"
    elif filter_department:
        filename += f"_{filter_department}"
    if filter_designation:
        filename += f"_{filter_designation}"
    if filter_name:
        filename += f"_{filter_name}"
    filename += f"_{attendance_date.strftime('%Y%m%d')}"
    filename = filename.replace(" ", "_")

    staff_members = Staff.objects.filter(status="active")

    if staff_id:
        staff_members = staff_members.filter(pk=staff_id)
    elif filter_department:
        staff_members = staff_members.filter(department__icontains=filter_department)
    if filter_designation:
        staff_members = staff_members.filter(designation__icontains=filter_designation)
    if filter_name:
        staff_members = staff_members.filter(name__icontains=filter_name)

    if sort == "desc":
        staff_members = staff_members.order_by("-name")
    else:
        staff_members = staff_members.order_by("name")

    attendance_records = StaffAttendance.objects.filter(date=attendance_date, staff__in=staff_members)
    attendance_data = {}
    remarks_data = {}
    for rec in attendance_records:
        attendance_data[rec.staff_id] = rec.status
        remarks_data[rec.staff_id] = rec.remarks

    status_display = dict(StaffAttendance.ATTENDANCE_STATUS_CHOICES)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Staff Name", "Department", "Designation", "Attendance Status", "Remarks"])

    for staff_member in staff_members:
        status_key = attendance_data.get(staff_member.pk, "")
        status_display_val = status_display.get(status_key, "-")
        if status_display_val == "-" and status_key:
            status_display_val = status_key
        writer.writerow([
            staff_member.staff_id,
            staff_member.name,
            staff_member.department or "-",
            staff_member.designation or "-",
            status_display_val,
            remarks_data.get(staff_member.pk, ""),
        ])

    return response


def attendance_report(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_gender = request.GET.get("filter_gender", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    filter_month = request.GET.get("filter_month", date.today().strftime("%Y-%m")).strip()
    sort = request.GET.get("sort", "asc")

    try:
        year, month = map(int, filter_month.split("-"))
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
    except ValueError:
        today = date.today()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        filter_month = today.strftime("%Y-%m")

    dates_in_month = []
    current = first_day
    while current <= last_day:
        dates_in_month.append(current)
        current += timedelta(days=1)

    students = Student.objects.select_related("school_class", "section").filter(status="active")
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

    if sort == "desc":
        students = students.order_by("-school_class__numeric_order", "-section__name", "-roll_no")
    else:
        students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    attendance_records = StudentAttendance.objects.filter(
        student__in=students,
        date__gte=first_day,
        date__lte=last_day,
    )

    attendance_matrix = {}
    for rec in attendance_records:
        if rec.student_id not in attendance_matrix:
            attendance_matrix[rec.student_id] = {}
        attendance_matrix[rec.student_id][rec.date] = rec.status

    student_stats = {}
    for student in students:
        present_count = 0
        late_count = 0
        absent_count = 0
        half_day_count = 0
        holiday_count = 0
        total_present_days = 0

        student_dates = attendance_matrix.get(student.pk, {})
        for d in dates_in_month:
            status = student_dates.get(d)
            if status == "present":
                present_count += 1
                total_present_days += 1
            elif status == "late":
                late_count += 1
                total_present_days += 1
            elif status == "absent":
                absent_count += 1
            elif status == "half_day":
                half_day_count += 1
                total_present_days += 0.5
            elif status == "holiday":
                holiday_count += 1

        total_working_days = len(dates_in_month) - holiday_count
        if total_working_days > 0:
            percentage = round((total_present_days / total_working_days) * 100)
        else:
            percentage = 0

        student_stats[student.pk] = {
            "present": present_count,
            "late": late_count,
            "absent": absent_count,
            "half_day": half_day_count,
            "holiday": holiday_count,
            "percentage": percentage,
        }

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")

    days_info = []
    for d in dates_in_month:
        days_info.append({
            "date": d,
            "day_num": d.day,
            "day_short": d.strftime("%a")[0],
        })

    context = {
        "students": students,
        "days_info": days_info,
        "attendance_matrix": attendance_matrix,
        "student_stats": student_stats,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_name": filter_name,
        "filter_gender": filter_gender,
        "filter_status": filter_status,
        "filter_month": filter_month,
        "sort": sort,
    }

    return render(request, "portaluser/people/attendance-report.html", context)


def attendance_report_export_pdf(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_month = request.GET.get("filter_month", date.today().strftime("%Y-%m")).strip()

    try:
        year, month = map(int, filter_month.split("-"))
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
    except ValueError:
        today = date.today()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        filter_month = today.strftime("%Y-%m")

    dates_in_month = []
    current = first_day
    while current <= last_day:
        dates_in_month.append(current)
        current += timedelta(days=1)

    students = Student.objects.select_related("school_class", "section").filter(status="active")
    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(section__name=filter_section)
    if filter_name:
        students = students.filter(name__icontains=filter_name)
    students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    attendance_records = StudentAttendance.objects.filter(
        student__in=students,
        date__gte=first_day,
        date__lte=last_day,
    )

    attendance_matrix = {}
    for rec in attendance_records:
        if rec.student_id not in attendance_matrix:
            attendance_matrix[rec.student_id] = {}
        attendance_matrix[rec.student_id][rec.date] = rec.status

    student_stats = {}
    for student in students:
        present_count = 0
        late_count = 0
        absent_count = 0
        half_day_count = 0
        holiday_count = 0
        total_present_days = 0

        student_dates = attendance_matrix.get(student.pk, {})
        for d in dates_in_month:
            status = student_dates.get(d)
            if status == "present":
                present_count += 1
                total_present_days += 1
            elif status == "late":
                late_count += 1
                total_present_days += 1
            elif status == "absent":
                absent_count += 1
            elif status == "half_day":
                half_day_count += 1
                total_present_days += 0.5
            elif status == "holiday":
                holiday_count += 1

        total_working_days = len(dates_in_month) - holiday_count
        if total_working_days > 0:
            percentage = round((total_present_days / total_working_days) * 100)
        else:
            percentage = 0

        student_stats[student.pk] = {
            "present": present_count,
            "late": late_count,
            "absent": absent_count,
            "half_day": half_day_count,
            "holiday": holiday_count,
            "percentage": percentage,
        }

    days_info = []
    for d in dates_in_month:
        days_info.append({
            "date": d,
            "day_num": d.day,
            "day_short": d.strftime("%a")[0],
        })

    title = "Attendance Report"
    if filter_class:
        title += f" - {filter_class}"
    if filter_section:
        title += f" - Section {filter_section}"
    title += f" ({first_day.strftime('%b %Y')})"

    context = {
        "title": title,
        "students": students,
        "days_info": days_info,
        "attendance_matrix": attendance_matrix,
        "student_stats": student_stats,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    }

    return render(request, "portaluser/people/attendance-report-print.html", context)


def attendance_report_export_excel(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_month = request.GET.get("filter_month", date.today().strftime("%Y-%m")).strip()

    try:
        year, month = map(int, filter_month.split("-"))
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
    except ValueError:
        today = date.today()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        filter_month = today.strftime("%Y-%m")

    dates_in_month = []
    current = first_day
    while current <= last_day:
        dates_in_month.append(current)
        current += timedelta(days=1)

    students = Student.objects.select_related("school_class", "section").filter(status="active")
    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(section__name=filter_section)
    if filter_name:
        students = students.filter(name__icontains=filter_name)
    students = students.order_by("school_class__numeric_order", "section__name", "roll_no")

    attendance_records = StudentAttendance.objects.filter(
        student__in=students,
        date__gte=first_day,
        date__lte=last_day,
    )

    attendance_matrix = {}
    for rec in attendance_records:
        if rec.student_id not in attendance_matrix:
            attendance_matrix[rec.student_id] = {}
        attendance_matrix[rec.student_id][rec.date] = rec.status

    status_display = dict(StudentAttendance.ATTENDANCE_STATUS_CHOICES)

    filename = "attendance_report"
    if filter_class:
        filename += f"_{filter_class}"
    if filter_section:
        filename += f"_{filter_section}"
    filename += f"_{first_day.strftime('%Y%m')}"
    filename = filename.replace(" ", "_")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    header = ["Admission No", "Roll No", "Student Name", "Class", "Section", "%", "P", "L", "A", "H", "F"]
    for d in dates_in_month:
        header.append(f"{d.day} {d.strftime('%a')}")
    writer.writerow(header)

    for student in students:
        student_dates = attendance_matrix.get(student.pk, {})
        present_count = 0
        late_count = 0
        absent_count = 0
        half_day_count = 0
        holiday_count = 0
        total_present_days = 0

        for d in dates_in_month:
            status = student_dates.get(d)
            if status == "present":
                present_count += 1
                total_present_days += 1
            elif status == "late":
                late_count += 1
                total_present_days += 1
            elif status == "absent":
                absent_count += 1
            elif status == "half_day":
                half_day_count += 1
                total_present_days += 0.5
            elif status == "holiday":
                holiday_count += 1

        total_working_days = len(dates_in_month) - holiday_count
        percentage = round((total_present_days / total_working_days) * 100) if total_working_days > 0 else 0

        row = [
            student.admission_no,
            student.roll_no or "-",
            student.name,
            student.school_class.name,
            student.section.name,
            percentage,
            present_count,
            late_count,
            absent_count,
            half_day_count,
            holiday_count,
        ]

        for d in dates_in_month:
            status = student_dates.get(d)
            if status:
                row.append(status_display.get(status, status))
            else:
                row.append("-")
        writer.writerow(row)

    return response

