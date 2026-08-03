import csv
from datetime import datetime, date

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from core.models import AcademicYear, School
from .models import Department, Designation, Holiday, LeaveType, LeaveRequest


def _parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def department_list(request):
    if request.method == "POST":
        if "add_department" in request.POST:
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            if not name:
                messages.error(request, "Department name is required.")
            elif Department.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Department '{name}' already exists.")
            else:
                Department.objects.create(name=name, is_active=is_active)
                messages.success(request, "Department added successfully.")
            return redirect("hrm:department-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Department.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} department(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("hrm:department-list")

    departments = Department.objects.all()

    filter_department = request.GET.get("filter_department", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_department:
        departments = departments.filter(name__iexact=filter_department)
    if filter_status == "active":
        departments = departments.filter(is_active=True)
    elif filter_status == "inactive":
        departments = departments.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        departments = departments.order_by("-name")
    elif sort in ("recent", "recent_added"):
        departments = departments.order_by("-created_at")
    else:
        departments = departments.order_by("name")

    department_options = (
        Department.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/hrm/departments.html", {
        "departments": departments,
        "department_options": department_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_department": filter_department,
        "filter_status": filter_status,
    })


def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            messages.error(request, "Department name is required.")
        elif Department.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f"Department '{name}' already exists.")
        else:
            department.name = name
            department.is_active = is_active
            department.save()
            messages.success(request, "Department updated successfully.")
    return redirect("hrm:department-list")


def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        department.delete()
        messages.success(request, "Department deleted successfully.")
    return redirect("hrm:department-list")


def designation_list(request):
    if request.method == "POST":
        if "add_designation" in request.POST:
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            if not name:
                messages.error(request, "Designation name is required.")
            elif Designation.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Designation '{name}' already exists.")
            else:
                Designation.objects.create(name=name, is_active=is_active)
                messages.success(request, "Designation added successfully.")
            return redirect("hrm:designation-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Designation.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} designation(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("hrm:designation-list")

    designations = Designation.objects.all()

    filter_designation = request.GET.get("filter_designation", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_designation:
        designations = designations.filter(name__iexact=filter_designation)
    if filter_status == "active":
        designations = designations.filter(is_active=True)
    elif filter_status == "inactive":
        designations = designations.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        designations = designations.order_by("-name")
    elif sort in ("recent", "recent_added"):
        designations = designations.order_by("-created_at")
    else:
        designations = designations.order_by("name")

    designation_options = (
        Designation.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/hrm/designation.html", {
        "designations": designations,
        "designation_options": designation_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_designation": filter_designation,
        "filter_status": filter_status,
    })


def designation_edit(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            messages.error(request, "Designation name is required.")
        elif Designation.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f"Designation '{name}' already exists.")
        else:
            designation.name = name
            designation.is_active = is_active
            designation.save()
            messages.success(request, "Designation updated successfully.")
    return redirect("hrm:designation-list")


def designation_delete(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    if request.method == "POST":
        designation.delete()
        messages.success(request, "Designation deleted successfully.")
    return redirect("hrm:designation-list")


def holiday_list(request):
    if request.method == "POST":
        if "add_holiday" in request.POST:
            title = request.POST.get("title", "").strip()
            date = _parse_date(request.POST.get("date", ""))
            description = request.POST.get("description", "").strip()
            is_active = request.POST.get("is_active") == "on"
            if not title:
                messages.error(request, "Holiday title is required.")
            elif not date:
                messages.error(request, "A valid holiday date is required.")
            elif Holiday.objects.filter(title__iexact=title, date=date).exists():
                messages.error(
                    request, f"Holiday '{title}' on {date.strftime('%d %b %Y')} already exists."
                )
            else:
                Holiday.objects.create(
                    title=title, date=date, description=description, is_active=is_active
                )
                messages.success(request, "Holiday added successfully.")
            return redirect("hrm:holiday-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Holiday.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} holiday(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("hrm:holiday-list")

    holidays = Holiday.objects.all()

    filter_holiday = request.GET.get("filter_holiday", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_holiday:
        holidays = holidays.filter(title__iexact=filter_holiday)
    if filter_status == "active":
        holidays = holidays.filter(is_active=True)
    elif filter_status == "inactive":
        holidays = holidays.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        holidays = holidays.order_by("-title")
    elif sort in ("recent", "recent_added"):
        holidays = holidays.order_by("-created_at")
    else:
        holidays = holidays.order_by("title")

    holiday_options = (
        Holiday.objects.values_list("title", flat=True).distinct().order_by("title")
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/hrm/holidays.html", {
        "holidays": holidays,
        "holiday_options": holiday_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_holiday": filter_holiday,
        "filter_status": filter_status,
    })


def holiday_edit(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        date = _parse_date(request.POST.get("date", ""))
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not title:
            messages.error(request, "Holiday title is required.")
        elif not date:
            messages.error(request, "A valid holiday date is required.")
        elif (
            Holiday.objects.filter(title__iexact=title, date=date)
            .exclude(pk=pk)
            .exists()
        ):
            messages.error(
                request, f"Holiday '{title}' on {date.strftime('%d %b %Y')} already exists."
            )
        else:
            holiday.title = title
            holiday.date = date
            holiday.description = description
            holiday.is_active = is_active
            holiday.save()
            messages.success(request, "Holiday updated successfully.")
    return redirect("hrm:holiday-list")


def holiday_delete(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == "POST":
        holiday.delete()
        messages.success(request, "Holiday deleted successfully.")
    return redirect("hrm:holiday-list")


def leave_list(request):
    if request.method == "POST":
        if "add_leave" in request.POST:
            name = request.POST.get("name", "").strip()
            is_active = request.POST.get("is_active") == "on"
            if not name:
                messages.error(request, "Leave Type name is required.")
            elif LeaveType.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Leave Type '{name}' already exists.")
            else:
                LeaveType.objects.create(name=name, is_active=is_active)
                messages.success(request, "Leave Type added successfully.")
            return redirect("hrm:leave-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                LeaveType.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} leave type(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("hrm:leave-list")

    leaves = LeaveType.objects.all()

    filter_leave = request.GET.get("filter_leave", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_leave:
        leaves = leaves.filter(name__iexact=filter_leave)
    if filter_status == "active":
        leaves = leaves.filter(is_active=True)
    elif filter_status == "inactive":
        leaves = leaves.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        leaves = leaves.order_by("-name")
    elif sort in ("recent", "recent_added"):
        leaves = leaves.order_by("-created_at")
    else:
        leaves = leaves.order_by("name")

    leave_options = (
        LeaveType.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/hrm/list-leaves.html", {
        "leaves": leaves,
        "leave_options": leave_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_leave": filter_leave,
        "filter_status": filter_status,
    })


def leave_edit(request, pk):
    leave = get_object_or_404(LeaveType, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            messages.error(request, "Leave Type name is required.")
        elif LeaveType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f"Leave Type '{name}' already exists.")
        else:
            leave.name = name
            leave.is_active = is_active
            leave.save()
            messages.success(request, "Leave Type updated successfully.")
    return redirect("hrm:leave-list")


def leave_delete(request, pk):
    leave = get_object_or_404(LeaveType, pk=pk)
    if request.method == "POST":
        leave.delete()
        messages.success(request, "Leave Type deleted successfully.")
    return redirect("hrm:leave-list")


def _parse_date_range(value):
    if not value:
        return None, None
    value = (value or "").strip()
    for sep in (" - ", " to ", "—"):
        if sep in value:
            parts = [p.strip() for p in value.split(sep) if p.strip()]
            if len(parts) == 2:
                return _parse_date(parts[0]), _parse_date(parts[1])
    return None, None


def _filtered_leave_requests(request):
    requests_qs = LeaveRequest.objects.all()

    filter_leave_type = request.GET.get("filter_leave_type", "").strip()
    filter_role = request.GET.get("filter_role", "").strip()
    filter_dates = request.GET.get("filter_dates", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_leave_type:
        requests_qs = requests_qs.filter(leave_type=filter_leave_type)
    if filter_role:
        requests_qs = requests_qs.filter(role__iexact=filter_role)
    if filter_status:
        requests_qs = requests_qs.filter(status=filter_status)
    if filter_dates:
        start, end = _parse_date_range(filter_dates)
        if start:
            requests_qs = requests_qs.filter(from_date__gte=start)
        if end:
            requests_qs = requests_qs.filter(to_date__lte=end)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        requests_qs = requests_qs.order_by("-applicant_name")
    elif sort in ("recent", "recent_viewed"):
        requests_qs = requests_qs.order_by("-applied_on", "-created_at")
    elif sort == "recent_added":
        requests_qs = requests_qs.order_by("-created_at")
    else:
        requests_qs = requests_qs.order_by("applicant_name")

    return requests_qs


def _redirect_to_list(request):
    """Redirect back to the approve request list preserving the current filters."""
    url = reverse("hrm:approve-request-list")
    query_string = request.META.get("QUERY_STRING", "")
    if query_string:
        url = f"{url}?{query_string}"
    return redirect(url)


def approve_request_list(request):
    if request.method == "POST":
        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                LeaveRequest.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} leave request(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return _redirect_to_list(request)

    requests_qs = _filtered_leave_requests(request)

    leave_type_choices = dict(LeaveRequest.LEAVE_TYPE_CHOICES)
    leave_type_options = [
        (value, leave_type_choices.get(value, value))
        for value in LeaveRequest.objects.values_list("leave_type", flat=True).distinct()
    ]

    role_options = (
        LeaveRequest.objects.exclude(role="")
        .values_list("role", flat=True)
        .distinct()
        .order_by("role")
    )

    status_choices = dict(LeaveRequest.STATUS_CHOICES)
    status_options = [
        (value, status_choices.get(value, value))
        for value in LeaveRequest.objects.values_list("status", flat=True).distinct()
    ]

    seen = set()
    date_options = []
    for req in LeaveRequest.objects.order_by("-from_date", "-to_date"):
        label = f"{req.from_date.strftime('%d %b %Y')} - {req.to_date.strftime('%d %b %Y')}"
        value = f"{req.from_date.isoformat()} - {req.to_date.isoformat()}"
        if value not in seen:
            seen.add(value)
            date_options.append({"label": label, "value": value})

    sort = request.GET.get("sort", "asc")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/hrm/approve-request.html", {
        "requests": requests_qs,
        "leave_type_options": leave_type_options,
        "role_options": role_options,
        "status_options": status_options,
        "date_options": date_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_leave_type": request.GET.get("filter_leave_type", "").strip(),
        "filter_role": request.GET.get("filter_role", "").strip(),
        "filter_dates": request.GET.get("filter_dates", "").strip(),
        "filter_status": request.GET.get("filter_status", "").strip(),
    })


def approve_request_update(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == "POST":
        status = request.POST.get("approval_status", "").strip()
        note = request.POST.get("note", "").strip()
        if status in dict(LeaveRequest.STATUS_CHOICES):
            leave_request.status = status
            leave_request.note = note
            leave_request.save()
            messages.success(
                request,
                f"Leave request of {leave_request.applicant_name} marked as "
                f"{leave_request.get_status_display()}.",
            )
        else:
            messages.error(request, "Invalid approval status selected.")
    return _redirect_to_list(request)


def approve_request_delete(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == "POST":
        leave_request.delete()
        messages.success(request, "Leave request deleted successfully.")
    return _redirect_to_list(request)


def approve_request_export_pdf(request):
    requests_qs = _filtered_leave_requests(request)
    school = School.objects.filter(is_active=True).first()
    return render(request, "portaluser/hrm/approve-request-print.html", {
        "requests": requests_qs,
        "school_name": school.name if school else "Global International",
        "title": "Approved Leave Request List",
    })


def approve_request_export_excel(request):
    requests_qs = _filtered_leave_requests(request)

    filename = f"approved_leave_requests_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Submitted By", "Leave Type", "Role", "Leave Date",
        "No of Days", "Applied On", "Authority", "Status",
    ])

    for req in requests_qs:
        submitted_by = req.applicant_name
        if req.applicant_id:
            submitted_by = f"{submitted_by} ({req.applicant_id})"
        writer.writerow([
            submitted_by,
            req.get_leave_type_display(),
            req.role or "-",
            f"{req.from_date.strftime('%d %b %Y')} - {req.to_date.strftime('%d %b %Y')}",
            req.no_of_days,
            req.applied_on.strftime("%d %b %Y") if req.applied_on else "-",
            req.authority or "-",
            req.get_status_display(),
        ])

    return response
