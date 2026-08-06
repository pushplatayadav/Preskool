import csv
import json
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from academics.models import SchoolClass, Section
from accounts.models import Role, User
from core.models import AcademicYear, School
from .models import Event, NoticeBoard

CATEGORY_STYLES = {
    "celebration": {
        "border": "border-warning",
        "color": "text-warning",
        "icon": "ti ti-cake",
        "badge_bg": "bg-warning-transparent",
        "calendar_bg": "#FFE9B8",
        "calendar_fg": "#B7791F",
    },
    "training": {
        "border": "border-success",
        "color": "text-success",
        "icon": "ti ti-clipboard-heart",
        "badge_bg": "bg-success-transparent",
        "calendar_bg": "#E4F7EB",
        "calendar_fg": "#1E9E5A",
    },
    "meeting": {
        "border": "border-info",
        "color": "text-info",
        "icon": "ti ti-users-group",
        "badge_bg": "bg-primary-transparent",
        "calendar_bg": "#E0F2FE",
        "calendar_fg": "#0369A1",
    },
    "holidays": {
        "border": "border-danger",
        "color": "text-danger",
        "icon": "ti ti-vacuum-cleaner",
        "badge_bg": "bg-danger-transparent",
        "calendar_bg": "#FBE3E3",
        "calendar_fg": "#E70D0D",
    },
    "camp": {
        "border": "border-secondary",
        "color": "text-secondary",
        "icon": "ti ti-campfire",
        "badge_bg": "bg-secondary-transparent",
        "calendar_bg": "#EDF2F4",
        "calendar_fg": "#0C4B5E",
    },
}

AVATAR_COLORS = [
    "bg-primary", "bg-success", "bg-warning", "bg-info",
    "bg-danger", "bg-secondary", "bg-purple", "bg-pink",
]

STANDARD_ROLES = [
    (Role.ADMIN, "Admin"),
    (Role.TEACHER, "Teacher"),
    (Role.STUDENT, "Student"),
    (Role.PARENT, "Parent"),
    (Role.GUARDIAN, "Guardian"),
    (Role.STAFF, "Staff"),
    (Role.ACCOUNTANT, "Accountant"),
    (Role.LIBRARIAN, "Librarian"),
    (Role.RECEPTIONIST, "Receptionist"),
    (Role.DRIVER, "Driver"),
]


def _seed_roles():
    """Create the standard built-in roles if they are missing (idempotent)."""
    for name, _label in STANDARD_ROLES:
        Role.objects.get_or_create(name=name)


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


def _parse_date_range(value):
    value = (value or "").strip()
    for sep in (" - ", " to ", "—"):
        if sep in value:
            parts = [p.strip() for p in value.split(sep) if p.strip()]
            if len(parts) == 2:
                return _parse_date(parts[0]), _parse_date(parts[1])
    return None, None


def _parse_time(value):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M", "%H:%M:%S", "%I %p", "%I%p"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def _base_events(request):
    events = Event.objects.select_related("added_by").prefetch_related(
        "classes", "sections", "roles", "teachers"
    )

    filter_category = request.GET.get("filter_category", "").strip()
    filter_event_for = request.GET.get("filter_event_for", "").strip()
    filter_dates = request.GET.get("filter_dates", "").strip()

    if filter_category in dict(Event.CATEGORY_CHOICES):
        events = events.filter(category=filter_category)
    if filter_event_for in dict(Event.EVENT_FOR_CHOICES):
        events = events.filter(event_for=filter_event_for)
    if filter_dates:
        start, end = _parse_date_range(filter_dates)
        if start:
            events = events.filter(start_date__gte=start)
        if end:
            events = events.filter(start_date__lte=end)

    return events.order_by("-start_date", "-created_at"), filter_category, filter_event_for, filter_dates


def _calendar_events(events):
    calendar_events = []
    for ev in events:
        styles = CATEGORY_STYLES.get(ev.category, CATEGORY_STYLES["meeting"])
        end = ev.end_date or ev.start_date
        calendar_events.append({
            "id": ev.pk,
            "title": ev.title,
            "start": ev.start_date.isoformat(),
            "end": (end + timedelta(days=1)).isoformat(),
            "allDay": True,
            "category": ev.category,
            "backgroundColor": styles["calendar_bg"],
            "borderColor": styles["calendar_fg"],
            "textColor": styles["calendar_fg"],
        })
    return calendar_events


def _event_details_json(events):
    details = {}
    for ev in events:
        details[str(ev.pk)] = {
            "id": ev.pk,
            "title": ev.title,
            "category": ev.get_category_display(),
            "category_key": ev.category,
            "event_for": ev.get_event_for_display(),
            "event_for_key": ev.event_for,
            "start_date": ev.start_date.strftime("%d %b %Y") if ev.start_date else "",
            "end_date": ev.end_date.strftime("%d %b %Y") if ev.end_date else "",
            "start_date_iso": ev.start_date.strftime("%d-%m-%Y") if ev.start_date else "",
            "end_date_iso": ev.end_date.strftime("%d-%m-%Y") if ev.end_date else "",
            "start_time": ev.start_time.strftime("%I:%M %p") if ev.start_time else "",
            "end_time": ev.end_time.strftime("%I:%M %p") if ev.end_time else "",
            "start_time_iso": ev.start_time.strftime("%I:%M %p") if ev.start_time else "",
            "end_time_iso": ev.end_time.strftime("%I:%M %p") if ev.end_time else "",
            "message": ev.message,
            "classes": ev.classes_display(),
            "sections": ev.sections_display(),
            "class_ids": [c.pk for c in ev.classes.all()],
            "section_ids": [s.pk for s in ev.sections.all()],
            "role_ids": [r.pk for r in ev.roles.all()],
            "teacher_ids": [t.pk for t in ev.teachers.all()],
            "roles": ev.roles_display(),
            "teachers": ev.teachers_names(),
            "attachment": ev.attachment.url if ev.attachment else "",
            "attachment_name": ev.attachment_name(),
        }
    return details


def _event_avatar_map(events):
    avatar_map = {}
    for ev in events:
        avatars = []
        for idx, teacher in enumerate(ev.teachers.all()[:3]):
            name = teacher.get_full_name() or teacher.username
            avatars.append({
                "initial": (name or "?")[0].upper(),
                "name": name,
                "color": AVATAR_COLORS[idx % len(AVATAR_COLORS)],
            })
        avatar_map[ev.pk] = avatars
    return avatar_map


def _base_notices(request):
    notices = NoticeBoard.objects.select_related("added_by").prefetch_related("message_to").all()

    filter_message_to = request.GET.get("filter_message_to", "").strip()
    filter_added_date = request.GET.get("filter_added_date", "").strip()
    filter_dates = request.GET.get("filter_dates", "").strip()

    if filter_message_to:
        notices = notices.filter(message_to__name=filter_message_to)
    if filter_added_date:
        parsed = _parse_date(filter_added_date)
        if parsed:
            notices = notices.filter(notice_date=parsed)
    if filter_dates:
        start, end = _parse_date_range(filter_dates)
        if start:
            notices = notices.filter(notice_date__gte=start)
        if end:
            notices = notices.filter(notice_date__lte=end)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        notices = notices.order_by("notice_date", "created_at")
    elif sort in ("recent", "recent_added"):
        notices = notices.order_by("-created_at")
    else:
        notices = notices.order_by("-notice_date", "-created_at")

    return notices, filter_message_to, filter_added_date, filter_dates, sort


def notice_board_list(request):
    _seed_roles()

    if request.method == "POST":
        if "add_message" in request.POST:
            title = request.POST.get("title", "").strip()
            notice_date = _parse_date(request.POST.get("notice_date", ""))
            publish_on = _parse_date(request.POST.get("publish_on", ""))
            message = request.POST.get("message", "").strip()
            role_ids = request.POST.getlist("message_to")

            if not title or not notice_date:
                messages.error(request, "Title and Notice Date are required.")
            else:
                notice = NoticeBoard.objects.create(
                    title=title,
                    notice_date=notice_date,
                    publish_on=publish_on,
                    message=message,
                    added_by=request.user if request.user.is_authenticated else None,
                )
                if request.FILES.get("attachment"):
                    notice.attachment = request.FILES["attachment"]
                if role_ids:
                    notice.message_to.set(role_ids)
                notice.save()
                messages.success(request, "Message added successfully.")
            return redirect("communication:notice-board")

        if "edit_message" in request.POST:
            notice = get_object_or_404(NoticeBoard, pk=request.POST.get("notice_id"))
            title = request.POST.get("title", "").strip()
            notice_date = _parse_date(request.POST.get("notice_date", ""))
            publish_on = _parse_date(request.POST.get("publish_on", ""))
            message = request.POST.get("message", "").strip()
            role_ids = request.POST.getlist("message_to")

            if not title or not notice_date:
                messages.error(request, "Title and Notice Date are required.")
            else:
                notice.title = title
                notice.notice_date = notice_date
                notice.publish_on = publish_on
                notice.message = message
                if request.FILES.get("attachment"):
                    notice.attachment = request.FILES["attachment"]
                notice.message_to.set(role_ids)
                notice.save()
                messages.success(request, "Message updated successfully.")
            return redirect("communication:notice-board")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                NoticeBoard.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} message(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("communication:notice-board")

    notices, filter_message_to, filter_added_date, filter_dates, sort = _base_notices(request)

    role_options = (
        Role.objects.order_by("name").values_list("name", flat=True)
    )

    seen = set()
    date_options = []
    for n in NoticeBoard.objects.order_by("-notice_date"):
        label = n.notice_date.strftime("%d %b %Y")
        value = n.notice_date.isoformat()
        if value not in seen:
            seen.add(value)
            date_options.append({"label": label, "value": value})

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    roles = Role.objects.all().order_by("name")
    role_pks = {r.name: r.pk for r in roles}

    return render(request, "portaluser/communication/notice-board.html", {
        "notices": notices,
        "roles": roles,
        "role_pks": role_pks,
        "role_options": role_options,
        "date_options": date_options,
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_message_to": filter_message_to,
        "filter_added_date": filter_added_date,
        "filter_dates": filter_dates,
    })


def notice_board_edit(request, pk):
    notice = get_object_or_404(NoticeBoard, pk=pk)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        notice_date = _parse_date(request.POST.get("notice_date", ""))
        publish_on = _parse_date(request.POST.get("publish_on", ""))
        message = request.POST.get("message", "").strip()
        role_ids = request.POST.getlist("message_to")

        if not title or not notice_date:
            messages.error(request, "Title and Notice Date are required.")
        else:
            notice.title = title
            notice.notice_date = notice_date
            notice.publish_on = publish_on
            notice.message = message
            if request.FILES.get("attachment"):
                notice.attachment = request.FILES["attachment"]
            notice.message_to.set(role_ids)
            notice.save()
            messages.success(request, "Message updated successfully.")
    return redirect("communication:notice-board")


def notice_board_delete(request, pk):
    notice = get_object_or_404(NoticeBoard, pk=pk)
    if request.method == "POST":
        notice.delete()
        messages.success(request, "Message deleted successfully.")
    return redirect("communication:notice-board")


def notice_board_export_pdf(request):
    notices, filter_message_to, filter_added_date, filter_dates, sort = _base_notices(request)
    school = School.objects.filter(is_active=True).first()

    title = "Notice Board Report"
    if filter_message_to:
        title += f" - Message To: {filter_message_to}"
    if filter_added_date:
        title += f" - Date: {filter_added_date}"

    return render(request, "portaluser/communication/notice-board-print.html", {
        "notices": notices,
        "school_name": school.name if school else "Global International",
        "current_academic_year": AcademicYear.objects.filter(is_current=True).first(),
        "title": title,
    })


def notice_board_export_excel(request):
    notices, filter_message_to, filter_added_date, filter_dates, sort = _base_notices(request)

    filename = f"notice_board_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Title", "Notice Date", "Publish On", "Message To",
        "Attachment", "Message", "Added By", "Added On",
    ])

    for n in notices:
        writer.writerow([
            n.title,
            n.notice_date.strftime("%d %b %Y") if n.notice_date else "-",
            n.publish_on.strftime("%d %b %Y") if n.publish_on else "-",
            n.message_to_names(),
            n.attachment_name() or "-",
            n.message or "-",
            n.added_by_name(),
            n.created_at.strftime("%d %b %Y %I:%M %p") if n.created_at else "-",
        ])

    return response


def events_list(request):
    _seed_roles()

    if request.method == "POST":
        if request.POST.get("add_event") == "1":
            title = request.POST.get("title", "").strip()
            start_date = _parse_date(request.POST.get("start_date", ""))
            if not title or not start_date:
                messages.error(request, "Title and Start Date are required.")
            else:
                event = Event.objects.create(
                    title=title,
                    event_for=request.POST.get("event_for", "all") or "all",
                    category=request.POST.get("category", "meeting") or "meeting",
                    start_date=start_date,
                    end_date=_parse_date(request.POST.get("end_date", "")),
                    start_time=_parse_time(request.POST.get("start_time", "")),
                    end_time=_parse_time(request.POST.get("end_time", "")),
                    message=request.POST.get("message", "").strip(),
                    added_by=request.user if request.user.is_authenticated else None,
                )
                if request.FILES.get("attachment"):
                    event.attachment = request.FILES["attachment"]
                class_id = request.POST.get("classes", "").strip()
                section_id = request.POST.get("sections", "").strip()
                role_ids = request.POST.getlist("roles")
                teacher_ids = request.POST.getlist("teachers")
                if class_id:
                    event.classes.add(class_id)
                if section_id:
                    event.sections.add(section_id)
                if role_ids:
                    event.roles.set(role_ids)
                if teacher_ids:
                    event.teachers.set(teacher_ids)
                event.save()
                messages.success(request, "Event added successfully.")
            return redirect("communication:events")

        if request.POST.get("edit_event") == "1":
            event = get_object_or_404(Event, pk=request.POST.get("event_id"))
            title = request.POST.get("title", "").strip()
            start_date = _parse_date(request.POST.get("start_date", ""))
            if not title or not start_date:
                messages.error(request, "Title and Start Date are required.")
            else:
                event.title = title
                event.event_for = request.POST.get("event_for", "all") or "all"
                event.category = request.POST.get("category", "meeting") or "meeting"
                event.start_date = start_date
                event.end_date = _parse_date(request.POST.get("end_date", ""))
                event.start_time = _parse_time(request.POST.get("start_time", ""))
                event.end_time = _parse_time(request.POST.get("end_time", ""))
                event.message = request.POST.get("message", "").strip()
                if request.FILES.get("attachment"):
                    event.attachment = request.FILES["attachment"]
                class_id = request.POST.get("classes", "").strip()
                section_id = request.POST.get("sections", "").strip()
                role_ids = request.POST.getlist("roles")
                teacher_ids = request.POST.getlist("teachers")
                event.classes.clear()
                event.sections.clear()
                if class_id:
                    event.classes.add(class_id)
                if section_id:
                    event.sections.add(section_id)
                event.roles.set(role_ids)
                event.teachers.set(teacher_ids)
                event.save()
                messages.success(request, "Event updated successfully.")
            return redirect("communication:events")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Event.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} event(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("communication:events")

    events, filter_category, filter_event_for, filter_dates = _base_events(request)

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()
    school_name = school.name if school else "Global International"

    classes = (
        SchoolClass.objects.filter(academic_year=current_academic_year).order_by("numeric_order")
        if current_academic_year
        else SchoolClass.objects.all().order_by("numeric_order")
    )
    sections = Section.objects.select_related("school_class").order_by(
        "school_class__numeric_order", "name"
    )
    roles = Role.objects.all().order_by("name")
    teacher_role = Role.objects.filter(name=Role.TEACHER).first()
    teachers = User.objects.filter(role=teacher_role).order_by("first_name", "username") if teacher_role else User.objects.none()

    category_options = [
        {
            "key": key,
            "label": label,
            "count": Event.objects.filter(category=key).count(),
            "style": CATEGORY_STYLES.get(key, CATEGORY_STYLES["meeting"]),
        }
        for key, label in Event.CATEGORY_CHOICES
    ]

    return render(request, "portaluser/communication/events.html", {
        "events": events,
        "calendar_events": json.dumps(_calendar_events(events)),
        "event_details": json.dumps(_event_details_json(events)),
        "avatar_map": _event_avatar_map(events),
        "category_options": category_options,
        "categories": Event.CATEGORY_CHOICES,
        "selected_category_label": dict(Event.CATEGORY_CHOICES).get(filter_category, ""),
        "category_styles": CATEGORY_STYLES,
        "avatar_colors": AVATAR_COLORS,
        "filter_category": filter_category,
        "filter_event_for": filter_event_for,
        "filter_dates": filter_dates,
        "classes": classes,
        "sections": sections,
        "roles": roles,
        "teachers": teachers,
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
        "school_name": school_name,
    })


def events_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        start_date = _parse_date(request.POST.get("start_date", ""))
        if not title or not start_date:
            messages.error(request, "Title and Start Date are required.")
        else:
            event.title = title
            event.event_for = request.POST.get("event_for", "all") or "all"
            event.category = request.POST.get("category", "meeting") or "meeting"
            event.start_date = start_date
            event.end_date = _parse_date(request.POST.get("end_date", ""))
            event.start_time = _parse_time(request.POST.get("start_time", ""))
            event.end_time = _parse_time(request.POST.get("end_time", ""))
            event.message = request.POST.get("message", "").strip()
            if request.FILES.get("attachment"):
                event.attachment = request.FILES["attachment"]
            class_id = request.POST.get("classes", "").strip()
            section_id = request.POST.get("sections", "").strip()
            role_ids = request.POST.getlist("roles")
            teacher_ids = request.POST.getlist("teachers")
            event.classes.clear()
            event.sections.clear()
            if class_id:
                event.classes.add(class_id)
            if section_id:
                event.sections.add(section_id)
            event.roles.set(role_ids)
            event.teachers.set(teacher_ids)
            event.save()
            messages.success(request, "Event updated successfully.")
    return redirect("communication:events")


def events_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
    return redirect("communication:events")


def events_export_pdf(request):
    events, filter_category, filter_event_for, filter_dates = _base_events(request)
    school = School.objects.filter(is_active=True).first()

    title = "Events Report"
    if filter_category:
        title += f" - Category: {dict(Event.CATEGORY_CHOICES).get(filter_category, filter_category)}"
    if filter_event_for:
        title += f" - Event For: {dict(Event.EVENT_FOR_CHOICES).get(filter_event_for, filter_event_for)}"

    return render(request, "portaluser/communication/events-print.html", {
        "events": events,
        "school_name": school.name if school else "Global International",
        "current_academic_year": AcademicYear.objects.filter(is_current=True).first(),
        "category_styles": CATEGORY_STYLES,
        "title": title,
    })


def events_export_excel(request):
    events, filter_category, filter_event_for, filter_dates = _base_events(request)

    filename = f"events_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "Title", "Event For", "Category", "Start Date", "End Date",
        "Start Time", "End Time", "Classes", "Sections", "Roles",
        "Teachers", "Attachment", "Message", "Added By", "Added On",
    ])

    for ev in events:
        writer.writerow([
            ev.title,
            ev.get_event_for_display(),
            ev.get_category_display(),
            ev.start_date.strftime("%d %b %Y") if ev.start_date else "-",
            ev.end_date.strftime("%d %b %Y") if ev.end_date else "-",
            ev.start_time.strftime("%I:%M %p") if ev.start_time else "-",
            ev.end_time.strftime("%I:%M %p") if ev.end_time else "-",
            ev.classes_display(),
            ev.sections_display(),
            ev.roles_display(),
            ", ".join(ev.teachers_names()) or "-",
            ev.attachment_name() or "-",
            ev.message or "-",
            ev.added_by_name(),
            ev.created_at.strftime("%d %b %Y %I:%M %p") if ev.created_at else "-",
        ])

    return response
