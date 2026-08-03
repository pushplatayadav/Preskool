from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse

from people.models import Student
from core.models import AcademicYear, School
from academics.models import SchoolClass, Section
from .models import Fees, FeesGroup, FeesType, FeesMaster, FeesAssign


def student_fees(request, pk):
    student = get_object_or_404(
        Student.objects.select_related("school_class", "section", "academic_year"),
        pk=pk,
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()

    languages = [lang.strip() for lang in student.languages_known.split(",") if lang.strip()]

    # Filter by academic year
    year_filter = request.GET.get("year", "")
    fees_qs = Fees.objects.filter(student=student).select_related("fees_group", "fees_type")
    if year_filter:
        fees_qs = fees_qs.filter(academic_year__name=year_filter)
    elif current_academic_year:
        fees_qs = fees_qs.filter(academic_year=current_academic_year)

    fees_qs = fees_qs.order_by("due_date")

    totals = fees_qs.aggregate(
        total_amount=Sum("amount"),
        total_discount=Sum("discount"),
        total_fine=Sum("fine"),
    )

    fees_groups = FeesGroup.objects.all().order_by("name")
    fees_types = FeesType.objects.all().order_by("name")

    if request.method == "POST":
        if "collect_fees" in request.POST:
            try:
                fees_group_id = request.POST.get("fees_group", "")
                fees_type_id = request.POST.get("fees_type", "")
                amount_str = request.POST.get("amount", "0")
                collection_date_str = request.POST.get("collection_date", "")
                payment_type = request.POST.get("payment_type", "cash")
                reference_no = request.POST.get("reference_no", "")
                is_paid = request.POST.get("is_paid") == "on"
                notes = request.POST.get("notes", "")

                amount = float(amount_str) if amount_str else 0

                collection_date = None
                if collection_date_str:
                    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
                        try:
                            collection_date = datetime.strptime(collection_date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                if not collection_date:
                    collection_date = date.today()

                fees_group = None
                if fees_group_id:
                    try:
                        fees_group = FeesGroup.objects.get(pk=fees_group_id)
                    except FeesGroup.DoesNotExist:
                        pass

                fees_type = None
                if fees_type_id:
                    try:
                        fees_type = FeesType.objects.get(pk=fees_type_id)
                    except FeesType.DoesNotExist:
                        pass

                fees_code = ""
                if fees_group:
                    fees_code = fees_group.name.lower().replace(" ", "-")
                if fees_type:
                    fees_code += "-" + fees_type.name.lower().replace(" ", "-")

                fees_code = fees_code.strip("-")

                Fees.objects.create(
                    student=student,
                    fees_group=fees_group,
                    fees_type=fees_type,
                    fees_code=fees_code,
                    due_date=collection_date,
                    amount=amount,
                    status="paid" if is_paid else "unpaid",
                    ref_id=reference_no,
                    payment_mode=payment_type,
                    date_paid=collection_date if is_paid else None,
                    discount=0,
                    fine=0,
                    notes=notes,
                    academic_year=current_academic_year,
                    collected_by=request.user if request.user.is_authenticated else None,
                )
                messages.success(request, "Fees collected successfully.")
            except Exception as e:
                messages.error(request, f"Error collecting fees: {str(e)}")
            return redirect("fees:student-fees", pk=student.pk)

        elif "delete_fee" in request.POST:
            fee_id = request.POST.get("fee_id")
            if fee_id:
                Fees.objects.filter(pk=fee_id, student=student).delete()
                messages.success(request, "Fee record deleted successfully.")
            return redirect("fees:student-fees", pk=student.pk)

    return render(request, "portaluser/fees/student-fees.html", {
        "student": student,
        "languages": languages,
        "fees": fees_qs,
        "total_amount": totals["total_amount"] or 0,
        "total_discount": totals["total_discount"] or 0,
        "total_fine": totals["total_fine"] or 0,
        "fees_groups": fees_groups,
        "fees_types": fees_types,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "year_filter": year_filter,
        "school_name": school.name if school else "Global International",
    })


def fees_group_list(request):
    if request.method == "POST":
        if "add_fees_group" in request.POST:
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()
            is_active = request.POST.get("is_active") == "on"
            if not name:
                messages.error(request, "Fees Group name is required.")
            elif FeesGroup.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Fees Group '{name}' already exists.")
            else:
                FeesGroup.objects.create(
                    name=name,
                    description=description,
                    is_active=is_active,
                )
                messages.success(request, "Fees Group added successfully.")
            return redirect("fees:fees-group-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                FeesGroup.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} fees group(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("fees:fees-group-list")

    fees_groups = FeesGroup.objects.all()

    filter_id = request.GET.get("filter_id", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_id:
        fees_groups = fees_groups.filter(code__icontains=filter_id)
    if filter_name:
        fees_groups = fees_groups.filter(name__iexact=filter_name)
    if filter_status == "active":
        fees_groups = fees_groups.filter(is_active=True)
    elif filter_status == "inactive":
        fees_groups = fees_groups.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        fees_groups = fees_groups.order_by("-name")
    elif sort in ("recent", "recent_added"):
        fees_groups = fees_groups.order_by("-created_at")
    else:
        fees_groups = fees_groups.order_by("name")

    id_options = (
        FeesGroup.objects.exclude(code="")
        .values_list("code", flat=True)
        .distinct()
        .order_by("-code")
    )
    name_options = (
        FeesGroup.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/fees/fees-group.html", {
        "fees_groups": fees_groups,
        "id_options": id_options,
        "name_options": name_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_id": filter_id,
        "filter_name": filter_name,
        "filter_status": filter_status,
    })


def fees_group_edit(request, pk):
    fees_group = get_object_or_404(FeesGroup, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            messages.error(request, "Fees Group name is required.")
        elif FeesGroup.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f"Fees Group '{name}' already exists.")
        else:
            fees_group.name = name
            fees_group.description = description
            fees_group.is_active = is_active
            fees_group.save()
            messages.success(request, "Fees Group updated successfully.")
    return redirect("fees:fees-group-list")


def fees_group_delete(request, pk):
    fees_group = get_object_or_404(FeesGroup, pk=pk)
    if request.method == "POST":
        fees_group.delete()
        messages.success(request, "Fees Group deleted successfully.")
    return redirect("fees:fees-group-list")


def fees_type_list(request):
    if request.method == "POST":
        if "add_fees_type" in request.POST:
            name = request.POST.get("name", "").strip()
            fees_group_id = request.POST.get("fees_group", "").strip()
            description = request.POST.get("description", "").strip()
            is_active = request.POST.get("is_active") == "on"
            if not name:
                messages.error(request, "Fees Type name is required.")
            elif FeesType.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Fees Type '{name}' already exists.")
            else:
                fees_group = None
                if fees_group_id:
                    try:
                        fees_group = FeesGroup.objects.get(pk=fees_group_id)
                    except FeesGroup.DoesNotExist:
                        pass
                FeesType.objects.create(
                    name=name,
                    fees_group=fees_group,
                    description=description,
                    is_active=is_active,
                )
                messages.success(request, "Fees Type added successfully.")
            return redirect("fees:fees-type-list")

        if "add_new_fees_group" in request.POST:
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()
            is_active = request.POST.get("is_active") == "on"
            error = ""
            if not name:
                error = "Fees Group name is required."
            elif FeesGroup.objects.filter(name__iexact=name).exists():
                error = f"Fees Group '{name}' already exists."

            is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
            if is_ajax:
                if error:
                    return JsonResponse({"success": False, "error": error})
                fees_group = FeesGroup.objects.create(
                    name=name,
                    description=description,
                    is_active=is_active,
                )
                return JsonResponse({"success": True, "id": fees_group.pk, "name": fees_group.name})
            if error:
                messages.error(request, error)
            else:
                FeesGroup.objects.create(
                    name=name,
                    description=description,
                    is_active=is_active,
                )
                messages.success(request, "Fees Group added successfully.")
            return redirect("fees:fees-type-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                FeesType.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} fees type(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("fees:fees-type-list")

    fees_types = FeesType.objects.select_related("fees_group")

    filter_id = request.GET.get("filter_id", "").strip()
    filter_name = request.GET.get("filter_name", "").strip()
    filter_group = request.GET.get("filter_group", "").strip()
    filter_type = request.GET.get("filter_type", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_id:
        fees_types = fees_types.filter(code__icontains=filter_id)
    if filter_name:
        fees_types = fees_types.filter(name__iexact=filter_name)
    if filter_group:
        fees_types = fees_types.filter(fees_group_id=filter_group)
    if filter_type:
        fees_types = fees_types.filter(name__iexact=filter_type)
    if filter_status == "active":
        fees_types = fees_types.filter(is_active=True)
    elif filter_status == "inactive":
        fees_types = fees_types.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        fees_types = fees_types.order_by("-name")
    elif sort in ("recent", "recent_added"):
        fees_types = fees_types.order_by("-created_at")
    else:
        fees_types = fees_types.order_by("name")

    id_options = (
        FeesType.objects.exclude(code="")
        .values_list("code", flat=True)
        .distinct()
        .order_by("-code")
    )
    name_options = (
        FeesType.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    group_options = (
        FeesGroup.objects.values("id", "name").distinct().order_by("name")
    )
    type_options = (
        FeesType.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    fees_groups = FeesGroup.objects.all().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/fees/fees-type.html", {
        "fees_types": fees_types,
        "fees_groups": fees_groups,
        "id_options": id_options,
        "name_options": name_options,
        "group_options": group_options,
        "type_options": type_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_id": filter_id,
        "filter_name": filter_name,
        "filter_group": filter_group,
        "filter_type": filter_type,
        "filter_status": filter_status,
    })


def fees_type_edit(request, pk):
    fees_type = get_object_or_404(FeesType, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        fees_group_id = request.POST.get("fees_group", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            messages.error(request, "Fees Type name is required.")
        elif FeesType.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f"Fees Type '{name}' already exists.")
        else:
            fees_type.name = name
            fees_type.description = description
            fees_type.is_active = is_active
            if fees_group_id:
                try:
                    fees_type.fees_group = FeesGroup.objects.get(pk=fees_group_id)
                except FeesGroup.DoesNotExist:
                    fees_type.fees_group = None
            else:
                fees_type.fees_group = None
            fees_type.save()
            messages.success(request, "Fees Type updated successfully.")
    return redirect("fees:fees-type-list")


def fees_type_delete(request, pk):
    fees_type = get_object_or_404(FeesType, pk=pk)
    if request.method == "POST":
        fees_type.delete()
        messages.success(request, "Fees Type deleted successfully.")
    return redirect("fees:fees-type-list")


def _parse_date(value):
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def fees_master_list(request):
    if request.method == "POST":
        if "add_fees_master" in request.POST:
            fees_group_id = request.POST.get("fees_group", "").strip()
            fees_type_id = request.POST.get("fees_type", "").strip()
            due_date_str = request.POST.get("due_date", "").strip()
            amount_str = request.POST.get("amount", "").strip()
            fine_type = request.POST.get("fine_type", "none").strip()
            fine_amount_str = request.POST.get(
                "fine_amount_fixed", ""
            ).strip() or request.POST.get("fine_amount_percentage", "").strip()
            is_active = request.POST.get("is_active") == "on"

            errors = []
            if not fees_group_id:
                errors.append("Fees Group is required.")
            if not fees_type_id:
                errors.append("Fees Type is required.")
            if not due_date_str:
                errors.append("Due Date is required.")
            elif not _parse_date(due_date_str):
                errors.append("Due Date is invalid.")

            amount = Decimal("0")
            if amount_str:
                try:
                    amount = Decimal(amount_str)
                except InvalidOperation:
                    errors.append("Amount must be a valid number.")

            fine_amount = Decimal("0")
            if fine_type != "none" and fine_amount_str:
                try:
                    fine_amount = Decimal(fine_amount_str)
                except InvalidOperation:
                    errors.append("Fine Amount must be a valid number.")

            if errors:
                messages.error(request, " ".join(errors))
            else:
                fees_group = FeesGroup.objects.filter(pk=fees_group_id).first()
                fees_type = FeesType.objects.filter(pk=fees_type_id).first()
                FeesMaster.objects.create(
                    fees_group=fees_group,
                    fees_type=fees_type,
                    due_date=_parse_date(due_date_str),
                    amount=amount,
                    fine_type=fine_type,
                    fine_amount=fine_amount,
                    is_active=is_active,
                )
                messages.success(request, "Fees Master added successfully.")
            return redirect("fees:fees-master-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                FeesMaster.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} fees master(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("fees:fees-master-list")

    fees_masters = FeesMaster.objects.select_related("fees_group", "fees_type")

    filter_id = request.GET.get("filter_id", "").strip()
    filter_group = request.GET.get("filter_group", "").strip()
    filter_type = request.GET.get("filter_type", "").strip()
    filter_due_date = request.GET.get("filter_due_date", "").strip()
    filter_fine_type = request.GET.get("filter_fine_type", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()

    if filter_id:
        fees_masters = fees_masters.filter(code__icontains=filter_id)
    if filter_group:
        fees_masters = fees_masters.filter(fees_group_id=filter_group)
    if filter_type:
        fees_masters = fees_masters.filter(fees_type_id=filter_type)
    if filter_due_date:
        parsed = _parse_date(filter_due_date)
        if parsed:
            fees_masters = fees_masters.filter(due_date=parsed)
    if filter_fine_type:
        fees_masters = fees_masters.filter(fine_type=filter_fine_type)
    if filter_status == "active":
        fees_masters = fees_masters.filter(is_active=True)
    elif filter_status == "inactive":
        fees_masters = fees_masters.filter(is_active=False)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        fees_masters = fees_masters.order_by("-fees_group__name")
    elif sort in ("recent", "recent_added"):
        fees_masters = fees_masters.order_by("-created_at")
    else:
        fees_masters = fees_masters.order_by("fees_group__name")

    id_options = (
        FeesMaster.objects.exclude(code="")
        .values_list("code", flat=True)
        .distinct()
        .order_by("-code")
    )
    group_options = (
        FeesGroup.objects.values_list("id", "name").distinct().order_by("name")
    )
    type_options = (
        FeesType.objects.values_list("id", "name").distinct().order_by("name")
    )
    due_date_options = (
        FeesMaster.objects.order_by("due_date")
        .values_list("due_date", flat=True)
        .distinct()
    )
    fees_groups = FeesGroup.objects.all().order_by("name")
    fees_types = FeesType.objects.all().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/fees/fees-master.html", {
        "fees_masters": fees_masters,
        "fees_groups": fees_groups,
        "fees_types": fees_types,
        "id_options": id_options,
        "group_options": group_options,
        "type_options": type_options,
        "due_date_options": due_date_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_id": filter_id,
        "filter_group": filter_group,
        "filter_type": filter_type,
        "filter_due_date": filter_due_date,
        "filter_fine_type": filter_fine_type,
        "filter_status": filter_status,
    })


def fees_master_edit(request, pk):
    fees_master = get_object_or_404(FeesMaster, pk=pk)
    if request.method == "POST":
        fees_group_id = request.POST.get("fees_group", "").strip()
        fees_type_id = request.POST.get("fees_type", "").strip()
        due_date_str = request.POST.get("due_date", "").strip()
        amount_str = request.POST.get("amount", "").strip()
        fine_type = request.POST.get("fine_type", "none").strip()
        fine_amount_str = request.POST.get(
            "fine_amount_fixed", ""
        ).strip() or request.POST.get("fine_amount_percentage", "").strip()
        is_active = request.POST.get("is_active") == "on"

        errors = []
        due_date = fees_master.due_date
        if due_date_str:
            parsed = _parse_date(due_date_str)
            if parsed:
                due_date = parsed
            else:
                errors.append("Due Date is invalid.")

        if amount_str:
            try:
                fees_master.amount = Decimal(amount_str)
            except InvalidOperation:
                errors.append("Amount must be a valid number.")

        if fine_type == "none":
            fees_master.fine_amount = Decimal("0")
        elif fine_amount_str:
            try:
                fees_master.fine_amount = Decimal(fine_amount_str)
            except InvalidOperation:
                errors.append("Fine Amount must be a valid number.")
        else:
            fees_master.fine_amount = Decimal("0")

        if not fees_group_id or not fees_type_id:
            errors.append("Fees Group and Fees Type are required.")

        if errors:
            messages.error(request, " ".join(errors))
        else:
            fees_master.fees_group = FeesGroup.objects.filter(
                pk=fees_group_id
            ).first()
            fees_master.fees_type = FeesType.objects.filter(pk=fees_type_id).first()
            fees_master.due_date = due_date
            fees_master.fine_type = fine_type
            if fine_type == "none":
                fees_master.fine_amount = Decimal("0")
            fees_master.is_active = is_active
            fees_master.save()
            messages.success(request, "Fees Master updated successfully.")
    return redirect("fees:fees-master-list")


def fees_master_delete(request, pk):
    fees_master = get_object_or_404(FeesMaster, pk=pk)
    if request.method == "POST":
        fees_master.delete()
        messages.success(request, "Fees Master deleted successfully.")
    return redirect("fees:fees-master-list")


def _build_fees_code(fees_group, fees_type):
    parts = []
    if fees_group:
        parts.append(fees_group.name.lower().replace(" ", "-"))
    if fees_type:
        parts.append(fees_type.name.lower().replace(" ", "-"))
    return "-".join([p for p in parts if p])


def _create_fees_for_assignment(student, fees_master, academic_year):
    """Create the unpaid Fees liability for a student if it does not already exist."""
    existing = Fees.objects.filter(
        student=student,
        fees_group=fees_master.fees_group,
        fees_type=fees_master.fees_type,
        academic_year=academic_year,
    ).first()
    if existing:
        return existing, False
    return Fees.objects.create(
        student=student,
        fees_group=fees_master.fees_group,
        fees_type=fees_master.fees_type,
        fees_code=_build_fees_code(fees_master.fees_group, fees_master.fees_type),
        due_date=fees_master.due_date or date.today(),
        amount=fees_master.amount,
        status="unpaid",
        academic_year=academic_year,
    ), True


def _infer_assignment_filters(students, class_id, section_id, gender, category):
    """Fill blank Class/Section/Gender/Category from the selected students."""
    students = list(students)
    if not class_id and students:
        class_ids = {s.school_class_id for s in students}
        if len(class_ids) == 1:
            class_id = class_ids.pop()
    if not section_id and students:
        section_ids = {s.section_id for s in students}
        if len(section_ids) == 1:
            section_id = section_ids.pop()
    if not gender and students:
        genders = {s.gender for s in students}
        if len(genders) == 1 and genders <= {"male", "female"}:
            gender = genders.pop()
    if not category and students:
        categories = {s.category for s in students if s.category}
        if len(categories) == 1:
            category = categories.pop()
    return class_id, section_id, gender, category


def fees_assign_list(request):
    if request.method == "POST":
        if "assign_fees" in request.POST:
            fee_ids = request.POST.getlist("fee_items")
            student_ids = request.POST.getlist("student_items")
            class_id = request.POST.get("class_id", "").strip()
            section_id = request.POST.get("section_id", "").strip()
            gender = request.POST.get("gender", "").strip()
            category = request.POST.get("category", "").strip()

            errors = []
            if not fee_ids:
                errors.append("Select at least one Fees Type.")
            if not student_ids:
                errors.append("Select at least one Student.")

            if errors:
                messages.error(request, " ".join(errors))
                return redirect("fees:fees-assign-list")

            current_year = AcademicYear.objects.filter(is_current=True).first()

            fees_masters = (
                FeesMaster.objects.filter(pk__in=fee_ids, is_active=True)
                .select_related("fees_group", "fees_type")
                .order_by("id")
            )
            students = Student.objects.filter(pk__in=student_ids).order_by(
                "school_class__numeric_order", "section__name", "roll_no"
            )

            if not fees_masters:
                messages.error(request, "No valid Fees Type selected.")
                return redirect("fees:fees-assign-list")
            if not students:
                messages.error(request, "No valid Students selected.")
                return redirect("fees:fees-assign-list")

            class_id, section_id, gender, category = _infer_assignment_filters(
                students, class_id, section_id, gender, category
            )
            school_class = None
            if class_id:
                school_class = SchoolClass.objects.filter(pk=class_id).first()
            section = None
            if section_id:
                section = Section.objects.filter(pk=section_id).first()

            created_fees = 0
            for fm in fees_masters:
                assign = FeesAssign.objects.create(
                    fees_group=fm.fees_group,
                    fees_type=fm.fees_type,
                    amount=fm.amount,
                    school_class=school_class,
                    section=section,
                    gender=gender,
                    category=category,
                    academic_year=current_year,
                )
                assign.assigned_students.set(students)
                for student in students:
                    _, created = _create_fees_for_assignment(student, fm, current_year)
                    if created:
                        created_fees += 1

            messages.success(
                request,
                f"{len(fees_masters)} Fees Type(s) assigned to {len(students)} student(s) "
                f"successfully ({created_fees} fee record(s) created).",
            )
            return redirect("fees:fees-assign-list")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                FeesAssign.objects.filter(pk__in=ids).delete()
                messages.success(
                    request, f"{len(ids)} fees assignment(s) deleted successfully."
                )
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("fees:fees-assign-list")

    fees_assigns = (
        FeesAssign.objects.select_related(
            "fees_group", "fees_type", "school_class", "section", "academic_year"
        )
        .prefetch_related("assigned_students")
        .all()
    )

    filter_section = request.GET.get("filter_section", "").strip()
    filter_gender = request.GET.get("filter_gender", "").strip()
    filter_category = request.GET.get("filter_category", "").strip()

    if filter_section:
        fees_assigns = fees_assigns.filter(section_id=filter_section)
    if filter_gender and filter_gender != "both":
        fees_assigns = fees_assigns.filter(gender=filter_gender)
    if filter_category:
        fees_assigns = fees_assigns.filter(category__iexact=filter_category)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        fees_assigns = fees_assigns.order_by("-fees_group__name", "-fees_type__name")
    elif sort in ("recent", "recent_added"):
        fees_assigns = fees_assigns.order_by("-created_at")
    else:
        fees_assigns = fees_assigns.order_by("fees_group__name", "fees_type__name")

    fees_groups = FeesGroup.objects.all().order_by("name")
    fees_types = FeesType.objects.all().order_by("name")
    classes = SchoolClass.objects.all().order_by("numeric_order")
    sections = Section.objects.select_related("school_class").all()
    fees_masters = (
        FeesMaster.objects.filter(is_active=True)
        .select_related("fees_group", "fees_type")
        .order_by("fees_type__name", "fees_group__name")
    )
    students = Student.objects.select_related(
        "school_class", "section"
    ).order_by("school_class__numeric_order", "section__name", "roll_no")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    category_options = (
        Student.objects.exclude(category="")
        .exclude(category__isnull=True)
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return render(request, "portaluser/fees/fees-assign.html", {
        "fees_assigns": fees_assigns,
        "fees_groups": fees_groups,
        "fees_types": fees_types,
        "classes": classes,
        "sections": sections,
        "fees_masters": fees_masters,
        "students": students,
        "category_options": category_options,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "sort": sort,
        "filter_section": filter_section,
        "filter_gender": filter_gender,
        "filter_category": filter_category,
    })


def fees_assign_edit(request, pk):
    assign = get_object_or_404(FeesAssign, pk=pk)
    if request.method == "POST":
        fee_ids = request.POST.getlist("fee_items")
        student_ids = request.POST.getlist("student_items")
        class_id = request.POST.get("class_id", "").strip()
        section_id = request.POST.get("section_id", "").strip()
        gender = request.POST.get("gender", "").strip()
        category = request.POST.get("category", "").strip()

        errors = []
        if not fee_ids:
            errors.append("Select at least one Fees Type.")
        if not student_ids:
            errors.append("Select at least one Student.")

        if errors:
            messages.error(request, " ".join(errors))
            return redirect("fees:fees-assign-list")

        current_year = AcademicYear.objects.filter(is_current=True).first()
        fees_masters = list(
            FeesMaster.objects.filter(pk__in=fee_ids, is_active=True)
            .select_related("fees_group", "fees_type")
            .order_by("id")
        )
        if not fees_masters:
            messages.error(request, "No valid Fees Type selected.")
            return redirect("fees:fees-assign-list")

        students = Student.objects.filter(pk__in=student_ids).order_by(
            "school_class__numeric_order", "section__name", "roll_no"
        )
        if not students:
            messages.error(request, "No valid Students selected.")
            return redirect("fees:fees-assign-list")

        class_id, section_id, gender, category = _infer_assignment_filters(
            students, class_id, section_id, gender, category
        )
        school_class = (
            SchoolClass.objects.filter(pk=class_id).first() if class_id else None
        )
        section = (
            Section.objects.filter(pk=section_id).first() if section_id else None
        )

        created_fees = 0

        # Update the current assignment with the first selected fees master
        first_fm = fees_masters[0]
        assign.fees_group = first_fm.fees_group
        assign.fees_type = first_fm.fees_type
        assign.amount = first_fm.amount
        assign.school_class = school_class
        assign.section = section
        assign.gender = gender
        assign.category = category
        assign.academic_year = current_year
        assign.save()
        assign.assigned_students.set(students)
        for student in students:
            _, created = _create_fees_for_assignment(student, first_fm, current_year)
            if created:
                created_fees += 1

        # Create assignments for any additional selected fees masters
        for fm in fees_masters[1:]:
            existing = (
                FeesAssign.objects.filter(
                    fees_group=fm.fees_group,
                    fees_type=fm.fees_type,
                    academic_year=current_year,
                )
                .exclude(pk=assign.pk)
                .first()
            )
            if existing:
                existing.assigned_students.add(*students)
            else:
                new_assign = FeesAssign.objects.create(
                    fees_group=fm.fees_group,
                    fees_type=fm.fees_type,
                    amount=fm.amount,
                    school_class=school_class,
                    section=section,
                    gender=gender,
                    category=category,
                    academic_year=current_year,
                )
                new_assign.assigned_students.set(students)
            for student in students:
                _, created = _create_fees_for_assignment(student, fm, current_year)
                if created:
                    created_fees += 1

        messages.success(
            request,
            f"Fees assignment updated successfully ({created_fees} new fee record(s) created).",
        )
    return redirect("fees:fees-assign-list")


def fees_assign_delete(request, pk):
    assign = get_object_or_404(FeesAssign, pk=pk)
    if request.method == "POST":
        assign.delete()
        messages.success(request, "Fees assignment deleted successfully.")
    return redirect("fees:fees-assign-list")


def fees_assign_search(request):
    """AJAX endpoint to dynamically filter Fees Master and Students."""
    fees_group_id = request.GET.get("fees_group", "").strip()
    fees_type_id = request.GET.get("fees_type", "").strip()
    class_id = request.GET.get("class_id", "").strip()
    section_id = request.GET.get("section_id", "").strip()
    gender = request.GET.get("gender", "").strip()
    category = request.GET.get("category", "").strip()

    fees_masters = (
        FeesMaster.objects.filter(is_active=True)
        .select_related("fees_group", "fees_type")
        .order_by("fees_type__name", "fees_group__name")
    )
    if fees_group_id:
        fees_masters = fees_masters.filter(fees_group_id=fees_group_id)
    if fees_type_id:
        fees_masters = fees_masters.filter(fees_type_id=fees_type_id)

    students = Student.objects.select_related(
        "school_class", "section"
    ).order_by("school_class__numeric_order", "section__name", "roll_no")
    if class_id:
        students = students.filter(school_class_id=class_id)
    if section_id:
        students = students.filter(section_id=section_id)
    if gender and gender != "both":
        students = students.filter(gender=gender)
    if category:
        students = students.filter(category__iexact=category)

    fees_data = [
        {
            "id": fm.pk,
            "name": fm.fees_type.name if fm.fees_type else "-",
            "group": fm.fees_group.name if fm.fees_group else "-",
            "amount": str(fm.amount),
        }
        for fm in fees_masters
    ]
    students_data = [
        {
            "id": s.pk,
            "admission_no": s.admission_no,
            "name": s.name,
            "image": s.profile_image.url if s.profile_image else "",
            "class": s.school_class.name if s.school_class else "-",
            "section": s.section.name if s.section else "-",
            "gender": s.get_gender_display(),
            "category": s.category or "-",
        }
        for s in students
    ]
    return JsonResponse({
        "success": True,
        "fees": fees_data,
        "students": students_data,
    })


def collect_fees(request):
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    academic_years = AcademicYear.objects.all().order_by("-start_date")
    school = School.objects.filter(is_active=True).first()
    school_name = school.name if school else "Global International"

    # ── Collect fees (POST) ──
    if request.method == "POST":
        if "collect_fees" in request.POST:
            student_id = request.POST.get("student_id", "").strip()
            student = Student.objects.filter(pk=student_id).first()
            if not student:
                messages.error(request, "Student not found.")
            else:
                try:
                    fees_group_id = request.POST.get("fees_group", "").strip()
                    fees_type_id = request.POST.get("fees_type", "").strip()
                    amount_str = request.POST.get("amount", "").strip()
                    collection_date_str = request.POST.get("collection_date", "").strip()
                    payment_type = request.POST.get("payment_type", "").strip()
                    reference_no = request.POST.get("reference_no", "").strip()
                    is_paid = request.POST.get("is_paid") == "on"
                    notes = request.POST.get("notes", "").strip()

                    amount = Decimal(amount_str) if amount_str else Decimal("0")

                    collection_date = None
                    if collection_date_str:
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
                            try:
                                collection_date = datetime.strptime(collection_date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                    if not collection_date:
                        collection_date = date.today()

                    fees_group = None
                    if fees_group_id:
                        fees_group = FeesGroup.objects.filter(pk=fees_group_id).first()
                    fees_type = None
                    if fees_type_id:
                        fees_type = FeesType.objects.filter(pk=fees_type_id).first()

                    fees_code = ""
                    if fees_group:
                        fees_code = fees_group.name.lower().replace(" ", "-")
                    if fees_type:
                        fees_code += "-" + fees_type.name.lower().replace(" ", "-")
                    fees_code = fees_code.strip("-")

                    if not payment_type:
                        payment_type = "cash"

                    # ── Settle existing unpaid fees when the payment is marked as paid ──
                    settled = False
                    if is_paid:
                        unpaid_qs = Fees.objects.filter(
                            student=student,
                            academic_year=current_academic_year,
                        ).exclude(status="paid")
                        if fees_type:
                            unpaid_qs = unpaid_qs.filter(fees_type=fees_type)
                        elif fees_group:
                            unpaid_qs = unpaid_qs.filter(fees_group=fees_group)
                        unpaid_fees = list(unpaid_qs.order_by("due_date"))

                        if unpaid_fees:
                            outstanding_total = sum(
                                (f.amount + f.fine) - f.discount for f in unpaid_fees
                            )
                            if amount >= outstanding_total:
                                collected_by = (
                                    request.user if request.user.is_authenticated else None
                                )
                                for fee in unpaid_fees:
                                    fee.status = "paid"
                                    fee.date_paid = collection_date
                                    fee.payment_mode = payment_type
                                    if reference_no:
                                        fee.ref_id = reference_no
                                    if notes:
                                        fee.notes = notes
                                    fee.collected_by = collected_by
                                    fee.save()
                                settled = True

                    if not settled:
                        Fees.objects.create(
                            student=student,
                            fees_group=fees_group,
                            fees_type=fees_type,
                            fees_code=fees_code,
                            due_date=collection_date,
                            amount=amount,
                            status="paid" if is_paid else "unpaid",
                            ref_id=reference_no,
                            payment_mode=payment_type,
                            date_paid=collection_date if is_paid else None,
                            discount=0,
                            fine=0,
                            notes=notes,
                            academic_year=current_academic_year,
                            collected_by=request.user if request.user.is_authenticated else None,
                        )
                    messages.success(request, f"Fees collected successfully for {student.name}.")
                except Exception as e:
                    messages.error(request, f"Error collecting fees: {str(e)}")
        return redirect("fees:collect-fees")

    # ── Filters ──
    filter_admission = request.GET.get("filter_admission", "").strip()
    filter_roll = request.GET.get("filter_roll", "").strip()
    filter_student = request.GET.get("filter_student", "").strip()
    filter_class = request.GET.get("filter_class", "").strip()
    filter_section = request.GET.get("filter_section", "").strip()
    filter_amount = request.GET.get("filter_amount", "").strip()
    filter_due_date = request.GET.get("filter_due_date", "").strip()
    year_filter = request.GET.get("year", "").strip()
    sort = request.GET.get("sort", "asc")

    students_qs = Student.objects.select_related("school_class", "section")

    if filter_admission:
        students_qs = students_qs.filter(admission_no=filter_admission)
    if filter_roll:
        students_qs = students_qs.filter(roll_no=filter_roll)
    if filter_student:
        students_qs = students_qs.filter(name__iexact=filter_student)
    if filter_class:
        students_qs = students_qs.filter(school_class_id=filter_class)
    if filter_section:
        students_qs = students_qs.filter(section_id=filter_section)

    students = list(
        students_qs.order_by("school_class__numeric_order", "section__name", "roll_no")
    )

    # ── Fee summaries (per student, for the selected academic year) ──
    fee_year = current_academic_year
    if year_filter:
        fee_year = AcademicYear.objects.filter(name=year_filter).first()

    fees_qs = Fees.objects.select_related("student")
    if fee_year:
        fees_qs = fees_qs.filter(academic_year=fee_year)

    fee_map = defaultdict(list)
    for fee in fees_qs:
        fee_map[fee.student_id].append(fee)

    rows = []
    for student in students:
        sfees = fee_map.get(student.pk, [])
        unpaid = [f for f in sfees if f.status != "paid"]
        paid = [f for f in sfees if f.status == "paid"]
        if unpaid:
            amount = sum((f.amount + f.fine) - f.discount for f in unpaid)
            last_date = max((f.due_date for f in unpaid), default=None)
            status = "unpaid"
        elif paid:
            amount = sum(f.amount for f in paid)
            last_date = max((f.due_date for f in paid), default=None)
            status = "paid"
        else:
            amount = Decimal("0")
            last_date = None
            status = "unpaid"
        rows.append({
            "student": student,
            "amount": amount,
            "last_date": last_date,
            "status": status,
        })

    # Filtering on computed values
    if filter_amount:
        try:
            amount_filter = Decimal(filter_amount)
            rows = [r for r in rows if r["amount"] == amount_filter]
        except InvalidOperation:
            pass

    if filter_due_date:
        parsed_date = _parse_date(filter_due_date)
        if parsed_date:
            rows = [r for r in rows if r["last_date"] == parsed_date]

    # Sorting
    if sort == "desc":
        rows.sort(key=lambda r: (r["student"].name or "").lower(), reverse=True)
    elif sort in ("recent", "recently_viewed", "recent_added"):
        rows.sort(key=lambda r: r["student"].created_at, reverse=True)
    else:
        rows.sort(key=lambda r: (r["student"].name or "").lower())

    # ── Filter dropdown options ──
    admission_options = (
        Student.objects.exclude(admission_no="")
        .values_list("admission_no", flat=True)
        .distinct()
        .order_by("admission_no")
    )
    roll_options = (
        Student.objects.exclude(roll_no="")
        .values_list("roll_no", flat=True)
        .distinct()
        .order_by("roll_no")
    )
    student_options = (
        Student.objects.values_list("name", flat=True).distinct().order_by("name")
    )
    class_options = SchoolClass.objects.all().order_by("numeric_order")
    section_options = (
        Section.objects.select_related("school_class")
        .all()
        .order_by("school_class__numeric_order", "name")
    )
    amount_options = sorted({r["amount"] for r in rows if r["amount"] > 0})
    due_date_options = sorted({r["last_date"] for r in rows if r["last_date"]})

    total_outstanding = sum(r["amount"] for r in rows if r["status"] == "unpaid")
    total_collected = sum(r["amount"] for r in rows if r["status"] == "paid")

    fees_groups = FeesGroup.objects.all().order_by("name")
    fees_types = FeesType.objects.all().order_by("name")

    preserved = {}
    if filter_admission:
        preserved["filter_admission"] = filter_admission
    if filter_roll:
        preserved["filter_roll"] = filter_roll
    if filter_student:
        preserved["filter_student"] = filter_student
    if filter_class:
        preserved["filter_class"] = filter_class
    if filter_section:
        preserved["filter_section"] = filter_section
    if filter_amount:
        preserved["filter_amount"] = filter_amount
    if filter_due_date:
        preserved["filter_due_date"] = filter_due_date
    base_query = urlencode(preserved)

    return render(request, "portaluser/fees/collect-fees.html", {
        "rows": rows,
        "current_academic_year": current_academic_year,
        "academic_years": academic_years,
        "school_name": school_name,
        "fees_groups": fees_groups,
        "fees_types": fees_types,
        "admission_options": admission_options,
        "roll_options": roll_options,
        "student_options": student_options,
        "class_options": class_options,
        "section_options": section_options,
        "amount_options": amount_options,
        "due_date_options": due_date_options,
        "filter_admission": filter_admission,
        "filter_roll": filter_roll,
        "filter_student": filter_student,
        "filter_class": filter_class,
        "filter_section": filter_section,
        "filter_amount": filter_amount,
        "filter_due_date": filter_due_date,
        "year_filter": year_filter,
        "sort": sort,
        "base_query": base_query,
        "total_outstanding": total_outstanding,
        "total_collected": total_collected,
    })
