from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from .models import SchoolClass, Section, Subject, HomeWork, Schedule, ClassRoom, TimeTableEntry, Syllabus, DAY_CHOICES
from people.models import Student
from .forms import SectionForm, HomeWorkForm, ScheduleForm, ClassRoomForm, TimeTableEntryForm, SubjectForm, SyllabusForm
from core.models import AcademicYear, School

User = get_user_model()


def _find_or_create_class(class_name):
    """Find or create a SchoolClass for the current academic year."""
    academic_year = AcademicYear.objects.filter(is_current=True).first()
    if not academic_year:
        academic_year = AcademicYear.objects.order_by("-start_date").first()
    if not academic_year:
        return None
    numeric_order = 0
    name_upper = class_name.strip().upper()
    roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
    if name_upper in roman_map:
        numeric_order = roman_map[name_upper]
    else:
        try:
            numeric_order = int(name_upper)
        except ValueError:
            numeric_order = SchoolClass.objects.filter(academic_year=academic_year).count() + 1
    school_class, _ = SchoolClass.objects.get_or_create(
        academic_year=academic_year,
        name=class_name.strip(),
        defaults={"numeric_order": numeric_order},
    )
    return school_class


def classes_list(request):
    if request.method == "POST":
        if "add_class" in request.POST:
            form = SectionForm(request.POST)
            if form.is_valid():
                school_class = _find_or_create_class(form.cleaned_data["class_name"])
                if school_class is None:
                    messages.error(request, "No academic year found. Please set an academic year first.")
                    return redirect("academics:class-list")
                section_name = form.cleaned_data["section_name"]
                if Section.objects.filter(school_class=school_class, name=section_name).exists():
                    messages.error(request, f"Section {section_name} already exists for class {school_class.name}.")
                    return redirect("academics:class-list")
                Section.objects.create(
                    school_class=school_class,
                    name=section_name,
                    no_of_students=form.cleaned_data["no_of_students"],
                    no_of_subjects=form.cleaned_data["no_of_subjects"],
                    room_number=form.cleaned_data["room_number"],
                    is_active=form.cleaned_data["is_active"],
                )
                messages.success(request, "Class added successfully.")
            else:
                messages.error(request, "Could not add class. Please check the form.")
            return redirect("academics:class-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Section.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} class(es) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("academics:class-list")

    sections = Section.objects.select_related("school_class").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_class:
        sections = sections.filter(school_class__name=filter_class)
    if filter_section:
        sections = sections.filter(name=filter_section)
    if filter_status == "active":
        sections = sections.filter(is_active=True)
    elif filter_status == "inactive":
        sections = sections.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        sections = sections.order_by("-school_class__numeric_order", "-name")
    else:
        sections = sections.order_by("school_class__numeric_order", "name")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/academics/classes.html", {
        "sections": sections,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_status": filter_status,
    })


def class_edit(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            school_class = _find_or_create_class(form.cleaned_data["class_name"])
            if school_class is None:
                messages.error(request, "No academic year found.")
                return redirect("academics:class-list")
            section_name = form.cleaned_data["section_name"]
            if Section.objects.filter(school_class=school_class, name=section_name).exclude(pk=pk).exists():
                messages.error(request, f"Section {section_name} already exists for class {school_class.name}.")
                return redirect("academics:class-list")
            section.school_class = school_class
            section.name = section_name
            section.no_of_students = form.cleaned_data["no_of_students"]
            section.no_of_subjects = form.cleaned_data["no_of_subjects"]
            section.room_number = form.cleaned_data["room_number"]
            section.is_active = form.cleaned_data["is_active"]
            section.save()
            messages.success(request, "Class updated successfully.")
        else:
            messages.error(request, "Could not update class.")
    return redirect("academics:class-list")


def class_delete(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        section.delete()
        messages.success(request, "Class deleted successfully.")
    return redirect("academics:class-list")


def homework_list(request):
    homeworks = HomeWork.objects.select_related("school_class", "section", "subject", "created_by").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_subject = request.GET.get("filter_subject", "").strip()
    filter_date = request.GET.get("filter_date", "").strip()

    if filter_class:
        homeworks = homeworks.filter(school_class__name=filter_class)
    if filter_section:
        homeworks = homeworks.filter(section__name=filter_section)
    if filter_subject:
        homeworks = homeworks.filter(subject__name=filter_subject)
    if filter_date:
        homeworks = homeworks.filter(homework_date=filter_date)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        homeworks = homeworks.order_by("-school_class__numeric_order", "-section__name", "-subject__name")
    else:
        homeworks = homeworks.order_by("school_class__numeric_order", "section__name", "subject__name")

    filter_class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    filter_section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    filter_subject_names = Subject.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    school_classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.all().order_by("school_class__numeric_order", "name")
    subjects = Subject.objects.all().order_by("name")

    if request.method == "POST" and "add_homework" in request.POST:
        form = HomeWorkForm(request.POST, request.FILES)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.created_by = request.user if request.user.is_authenticated else None
            homework.save()
            messages.success(request, "Home Work added successfully.")
        else:
            messages.error(request, "Could not add home work. Please check the form.")
        return redirect("academics:homework-list")

    return render(request, "portaluser/academics/class-home-work.html", {
        "homeworks": homeworks,
        "class_names": filter_class_names,
        "section_names": filter_section_names,
        "subject_names": filter_subject_names,
        "school_classes": school_classes,
        "sections": sections,
        "subjects": subjects,
        "current_academic_year": current_academic_year,
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_subject": filter_subject,
        "filter_date": filter_date,
    })


def homework_edit(request, pk):
    homework = get_object_or_404(HomeWork, pk=pk)
    if request.method == "POST":
        form = HomeWorkForm(request.POST, request.FILES, instance=homework)
        if form.is_valid():
            form.save()
            messages.success(request, "Home Work updated successfully.")
        else:
            messages.error(request, "Could not update home work.")
    return redirect("academics:homework-list")


def homework_delete(request, pk):
    homework = get_object_or_404(HomeWork, pk=pk)
    if request.method == "POST":
        homework.delete()
        messages.success(request, "Home Work deleted successfully.")
    return redirect("academics:homework-list")


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

    return render(request, "portaluser/academics/class-report.html", {
        "sections": sections,
        "class_names": class_names,
        "section_names": section_names,
        "student_count_options": student_count_options,
        "current_academic_year": current_academic_year,
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


def schedule_list(request):
    if request.method == "POST":
        if "add_schedule" in request.POST:
            form = ScheduleForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Schedule added successfully.")
            else:
                messages.error(request, "Could not add schedule. Please check the form.")
            return redirect("academics:schedule-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Schedule.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} schedule(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("academics:schedule-list")

    schedules = Schedule.objects.all()

    filter_status = request.GET.get("filter_status", "").strip()
    filter_type = request.GET.get("filter_type", "").strip()

    if filter_status == "active":
        schedules = schedules.filter(status="active")
    elif filter_status == "inactive":
        schedules = schedules.filter(status="inactive")
    if filter_type:
        schedules = schedules.filter(schedule_type=filter_type)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        schedules = schedules.order_by("-start_time")
    elif sort == "recent":
        schedules = schedules.order_by("-created_at")
    elif sort == "recent_added":
        schedules = schedules.order_by("-created_at")
    else:
        schedules = schedules.order_by("start_time")

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/academics/schedule-classes.html", {
        "schedules": schedules,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_status": filter_status,
        "filter_type": filter_type,
    })


def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Schedule updated successfully.")
        else:
            messages.error(request, "Could not update schedule.")
    return redirect("academics:schedule-list")


def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == "POST":
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
    return redirect("academics:schedule-list")


def schedule_availability(request):
    schedules = Schedule.objects.all().values("id", "schedule_id", "schedule_type", "start_time", "end_time", "status")
    return JsonResponse({"schedules": list(schedules)})


def classroom_list(request):
    if request.method == "POST" and "add_classroom" in request.POST:
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class Room added successfully.")
        else:
            messages.error(request, "Could not add class room. Please check the form.")
        return redirect("academics:classroom-list")

    classrooms = ClassRoom.objects.all()

    filter_room = request.GET.get("filter_room", "").strip()
    filter_capacity = request.GET.get("filter_capacity", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_room:
        classrooms = classrooms.filter(room_number=filter_room)
    if filter_capacity:
        try:
            classrooms = classrooms.filter(capacity=int(filter_capacity))
        except ValueError:
            pass
    if filter_status == "active":
        classrooms = classrooms.filter(status="active")
    elif filter_status == "inactive":
        classrooms = classrooms.filter(status="inactive")

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        classrooms = classrooms.order_by("-room_number")
    else:
        classrooms = classrooms.order_by("room_number")

    room_numbers = ClassRoom.objects.values_list("room_number", flat=True).distinct().order_by("room_number")
    capacity_options = ClassRoom.objects.values_list("capacity", flat=True).distinct().order_by("capacity")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    return render(request, "portaluser/academics/class-room.html", {
        "classrooms": classrooms,
        "room_numbers": room_numbers,
        "capacity_options": capacity_options,
        "current_academic_year": current_academic_year,
        "sort": sort,
        "filter_room": filter_room,
        "filter_capacity": filter_capacity,
        "filter_status": filter_status,
    })


def classroom_edit(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == "POST":
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, "Class Room updated successfully.")
        else:
            messages.error(request, "Could not update class room.")
    return redirect("academics:classroom-list")


def classroom_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == "POST":
        classroom.delete()
        messages.success(request, "Class Room deleted successfully.")
    return redirect("academics:classroom-list")


def class_routine_list(request):
    if request.method == "POST" and "add_routine" in request.POST:
        form = TimeTableEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class Routine added successfully.")
        else:
            messages.error(request, "Could not add class routine. Please check the form.")
        return redirect("academics:classroutine-list")

    routines = TimeTableEntry.objects.select_related("school_class", "section", "subject", "teacher", "room").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_teacher = request.GET.get("filter_teacher", "").strip()
    filter_room = request.GET.get("filter_room", "").strip()
    filter_day = request.GET.get("filter_day", "").strip()

    if filter_class:
        routines = routines.filter(school_class__name=filter_class)
    if filter_section:
        routines = routines.filter(section__name=filter_section)
    if filter_teacher:
        routines = routines.filter(teacher__id=filter_teacher)
    if filter_room:
        routines = routines.filter(room__room_number=filter_room)
    if filter_day:
        routines = routines.filter(day=filter_day)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        routines = routines.order_by("-day", "-start_time")
    else:
        routines = routines.order_by("day", "start_time")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    teacher_list = User.objects.filter(is_staff=True).order_by("first_name", "last_name")
    room_numbers = ClassRoom.objects.values_list("room_number", flat=True).distinct().order_by("room_number")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    school_classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.all().order_by("school_class__numeric_order", "name")
    subjects = Subject.objects.all().order_by("name")
    teachers = User.objects.filter(is_staff=True).order_by("first_name", "last_name")
    classrooms = ClassRoom.objects.filter(status="active").order_by("room_number")

    return render(request, "portaluser/academics/class-routine.html", {
        "routines": routines,
        "class_names": class_names,
        "section_names": section_names,
        "teacher_list": teacher_list,
        "room_numbers": room_numbers,
        "current_academic_year": current_academic_year,
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_teacher": filter_teacher,
        "filter_room": filter_room,
        "filter_day": filter_day,
        "school_classes": school_classes,
        "sections": sections,
        "subjects": subjects,
        "teachers": teachers,
        "classrooms": classrooms,
        "day_choices": DAY_CHOICES,
    })


def class_routine_edit(request, pk):
    routine = get_object_or_404(TimeTableEntry, pk=pk)
    if request.method == "POST":
        form = TimeTableEntryForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, "Class Routine updated successfully.")
        else:
            messages.error(request, "Could not update class routine.")
    return redirect("academics:classroutine-list")


def class_routine_delete(request, pk):
    routine = get_object_or_404(TimeTableEntry, pk=pk)
    if request.method == "POST":
        routine.delete()
        messages.success(request, "Class Routine deleted successfully.")
    return redirect("academics:classroutine-list")


def section_list(request):
    if request.method == "POST":
        if "add_section" in request.POST:
            form = SectionForm(request.POST)
            if form.is_valid():
                school_class = _find_or_create_class(form.cleaned_data["class_name"])
                if school_class is None:
                    messages.error(request, "No academic year found. Please set an academic year first.")
                    return redirect("academics:section-list")
                section_name = form.cleaned_data["section_name"]
                if Section.objects.filter(school_class=school_class, name=section_name).exists():
                    messages.error(request, f"Section {section_name} already exists for class {school_class.name}.")
                    return redirect("academics:section-list")
                Section.objects.create(
                    school_class=school_class,
                    name=section_name,
                    no_of_students=form.cleaned_data["no_of_students"],
                    no_of_subjects=form.cleaned_data["no_of_subjects"],
                    room_number=form.cleaned_data["room_number"],
                    is_active=form.cleaned_data["is_active"],
                )
                messages.success(request, "Section added successfully.")
            else:
                messages.error(request, "Could not add section. Please check the form.")
            return redirect("academics:section-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Section.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} section(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("academics:section-list")

    sections = Section.objects.select_related("school_class").all()

    filter_section = request.GET.get("filter_section", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_section:
        sections = sections.filter(name=filter_section)
    if filter_status == "active":
        sections = sections.filter(is_active=True)
    elif filter_status == "inactive":
        sections = sections.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        sections = sections.order_by("-name")
    else:
        sections = sections.order_by("name")

    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/academics/class-section.html", {
        "sections": sections,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_section": filter_section,
        "filter_status": filter_status,
    })


def section_edit(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            school_class = _find_or_create_class(form.cleaned_data["class_name"])
            if school_class is None:
                messages.error(request, "No academic year found.")
                return redirect("academics:section-list")
            section_name = form.cleaned_data["section_name"]
            if Section.objects.filter(school_class=school_class, name=section_name).exclude(pk=pk).exists():
                messages.error(request, f"Section {section_name} already exists for class {school_class.name}.")
                return redirect("academics:section-list")
            section.school_class = school_class
            section.name = section_name
            section.no_of_students = form.cleaned_data["no_of_students"]
            section.no_of_subjects = form.cleaned_data["no_of_subjects"]
            section.room_number = form.cleaned_data["room_number"]
            section.is_active = form.cleaned_data["is_active"]
            section.save()
            messages.success(request, "Section updated successfully.")
        else:
            messages.error(request, "Could not update section.")
    return redirect("academics:section-list")


def section_delete(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        section.delete()
        messages.success(request, "Section deleted successfully.")
    return redirect("academics:section-list")


def subject_list(request):
    if request.method == "POST":
        if "add_subject" in request.POST:
            form = SubjectForm(request.POST)
            if form.is_valid():
                academic_year = AcademicYear.objects.filter(is_current=True).first()
                if not academic_year:
                    academic_year = AcademicYear.objects.order_by("-start_date").first()
                if not academic_year:
                    messages.error(request, "No academic year found. Please set an academic year first.")
                    return redirect("academics:subject-list")
                subject = Subject.objects.create(
                    academic_year=academic_year,
                    name=form.cleaned_data["name"],
                    code=form.cleaned_data["code"],
                    type=form.cleaned_data["type"],
                    is_active=form.cleaned_data["is_active"],
                )
                messages.success(request, "Subject added successfully.")
            else:
                messages.error(request, "Could not add subject. Please check the form.")
            return redirect("academics:subject-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Subject.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} subject(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("academics:subject-list")

    subjects = Subject.objects.all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_code = request.GET.get("filter_code", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_name:
        subjects = subjects.filter(name=filter_name)
    if filter_code:
        subjects = subjects.filter(code=filter_code)
    if filter_status == "active":
        subjects = subjects.filter(is_active=True)
    elif filter_status == "inactive":
        subjects = subjects.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        subjects = subjects.order_by("-name")
    else:
        subjects = subjects.order_by("name")

    subject_names = Subject.objects.values_list("name", flat=True).distinct().order_by("name")
    subject_codes = Subject.objects.values_list("code", flat=True).distinct().order_by("code")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/academics/class-subject.html", {
        "subjects": subjects,
        "subject_names": subject_names,
        "subject_codes": subject_codes,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_name": filter_name,
        "filter_code": filter_code,
        "filter_status": filter_status,
    })


def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject.name = form.cleaned_data["name"]
            subject.code = form.cleaned_data["code"]
            subject.type = form.cleaned_data["type"]
            subject.is_active = form.cleaned_data["is_active"]
            subject.save()
            messages.success(request, "Subject updated successfully.")
        else:
            messages.error(request, "Could not update subject.")
    return redirect("academics:subject-list")


def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        subject.delete()
        messages.success(request, "Subject deleted successfully.")
    return redirect("academics:subject-list")


def syllabus_list(request):
    if request.method == "POST":
        if "add_syllabus" in request.POST:
            form = SyllabusForm(request.POST, request.FILES)
            if form.is_valid():
                syllabus = form.save(commit=False)
                syllabus.title = syllabus.subject_group
                syllabus.save()
                messages.success(request, "Subject Group added successfully.")
            else:
                messages.error(request, "Could not add subject group. Please check the form.")
            return redirect("academics:syllabus-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Syllabus.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} subject group(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("academics:syllabus-list")

    syllabi = Syllabus.objects.select_related("school_class", "section").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_class:
        syllabi = syllabi.filter(school_class__name=filter_class)
    if filter_section:
        syllabi = syllabi.filter(section__name=filter_section)
    if filter_status == "active":
        syllabi = syllabi.filter(status="active")
    elif filter_status == "inactive":
        syllabi = syllabi.filter(status="inactive")

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        syllabi = syllabi.order_by("-school_class__numeric_order", "-section__name", "-uploaded_at")
    elif sort == "recent":
        syllabi = syllabi.order_by("-uploaded_at")
    elif sort == "recent_added":
        syllabi = syllabi.order_by("-uploaded_at")
    else:
        syllabi = syllabi.order_by("school_class__numeric_order", "section__name", "uploaded_at")

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    school_classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.all().order_by("school_class__numeric_order", "name")

    return render(request, "portaluser/academics/class-syllabus.html", {
        "syllabi": syllabi,
        "class_names": class_names,
        "section_names": section_names,
        "school_classes": school_classes,
        "sections": sections,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_status": filter_status,
    })


def syllabus_edit(request, pk):
    syllabus = get_object_or_404(Syllabus, pk=pk)
    if request.method == "POST":
        form = SyllabusForm(request.POST, request.FILES, instance=syllabus)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.title = updated.subject_group
            updated.save()
            messages.success(request, "Subject Group updated successfully.")
        else:
            messages.error(request, "Could not update subject group.")
    return redirect("academics:syllabus-list")


def syllabus_delete(request, pk):
    syllabus = get_object_or_404(Syllabus, pk=pk)
    if request.method == "POST":
        syllabus.delete()
        messages.success(request, "Subject Group deleted successfully.")
    return redirect("academics:syllabus-list")


def class_time_table(request):
    entries = TimeTableEntry.objects.select_related("school_class", "section", "subject", "teacher", "room").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()

    if filter_class:
        entries = entries.filter(school_class__name=filter_class)
    if filter_section:
        entries = entries.filter(section__name=filter_section)

    entries = entries.order_by("day", "start_time")

    timetable = {}
    for entry in entries:
        day = entry.day
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(entry)

    time_slots = []
    seen = set()
    for entry in entries:
        slot_key = (entry.start_time.strftime("%H:%M"), entry.end_time.strftime("%H:%M"))
        if slot_key not in seen:
            seen.add(slot_key)
            time_slots.append({
                "start": entry.start_time,
                "end": entry.end_time,
                "start_str": entry.start_time.strftime("%I:%M %p"),
                "end_str": entry.end_time.strftime("%I:%M %p"),
            })
    time_slots.sort(key=lambda x: x["start"])

    DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat"]
    DAY_NAMES = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday", "fri": "Friday", "sat": "Saturday"}

    timetable_grid = []
    for day_code in DAY_ORDER:
        day_entries = timetable.get(day_code, [])
        slot_map = {}
        for e in day_entries:
            slot_key = (e.start_time.strftime("%H:%M"), e.end_time.strftime("%H:%M"))
            slot_map[slot_key] = e
        rows = []
        for ts in time_slots:
            key = (ts["start"].strftime("%H:%M"), ts["end"].strftime("%H:%M"))
            rows.append(slot_map.get(key, None))
        timetable_grid.append({"code": day_code, "name": DAY_NAMES[day_code], "entries": rows})

    class_names = SchoolClass.objects.values_list("name", flat=True).distinct().order_by("name")
    section_names = Section.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/academics/class-time-table.html", {
        "timetable_grid": timetable_grid,
        "time_slots": time_slots,
        "class_names": class_names,
        "section_names": section_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "filter_class": filter_class,
        "filter_section": filter_section,
        "day_names": DAY_NAMES,
        "day_order": DAY_ORDER,
    })


def syllabus_export(request):
    syllabi = Syllabus.objects.select_related("school_class", "section").all()

    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_class:
        syllabi = syllabi.filter(school_class__name=filter_class)
    if filter_section:
        syllabi = syllabi.filter(section__name=filter_section)
    if filter_status == "active":
        syllabi = syllabi.filter(status="active")
    elif filter_status == "inactive":
        syllabi = syllabi.filter(status="inactive")

    syllabi = syllabi.order_by("school_class__numeric_order", "section__name", "uploaded_at")

    data = []
    for s in syllabi:
        data.append({
            "class": s.school_class.name,
            "section": s.section.name if s.section else "-",
            "subject_group": s.subject_group,
            "created_date": s.uploaded_at.strftime("%d %b %Y") if s.uploaded_at else "-",
            "status": s.get_status_display(),
        })

    return JsonResponse({"syllabi": data})


def student_time_table(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("school_class", "section"),
        pk=pk,
    )

    entries = TimeTableEntry.objects.select_related(
        "school_class", "section", "subject", "teacher", "room"
    ).filter(
        school_class=student.school_class,
        section=student.section,
    ).order_by("day", "start_time")

    timetable = {}
    for entry in entries:
        day = entry.day
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(entry)

    time_slots = []
    seen = set()
    for entry in entries:
        slot_key = (entry.start_time.strftime("%H:%M"), entry.end_time.strftime("%H:%M"))
        if slot_key not in seen:
            seen.add(slot_key)
            time_slots.append({
                "start": entry.start_time,
                "end": entry.end_time,
                "start_str": entry.start_time.strftime("%I:%M %p"),
                "end_str": entry.end_time.strftime("%I:%M %p"),
            })
    time_slots.sort(key=lambda x: x["start"])

    DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat"]
    DAY_NAMES = {
        "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday",
        "thu": "Thursday", "fri": "Friday", "sat": "Saturday",
    }

    timetable_grid = []
    for day_code in DAY_ORDER:
        day_entries = timetable.get(day_code, [])
        slot_map = {}
        for e in day_entries:
            slot_key = (e.start_time.strftime("%H:%M"), e.end_time.strftime("%H:%M"))
            slot_map[slot_key] = e
        rows = []
        for ts in time_slots:
            key = (ts["start"].strftime("%H:%M"), ts["end"].strftime("%H:%M"))
            rows.append(slot_map.get(key, None))
        timetable_grid.append({"code": day_code, "name": DAY_NAMES[day_code], "entries": rows})

    siblings = Student.objects.filter(
        school_class=student.school_class,
        section=student.section,
    ).exclude(pk=student.pk).select_related("school_class", "section")[:5]

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    languages = [lang.strip() for lang in student.languages_known.split(",") if lang.strip()]

    return render(request, "portaluser/academics/student-time-table.html", {
        "student": student,
        "timetable_grid": timetable_grid,
        "time_slots": time_slots,
        "siblings": siblings,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "day_names": DAY_NAMES,
        "day_order": DAY_ORDER,
        "languages": languages,
    })



