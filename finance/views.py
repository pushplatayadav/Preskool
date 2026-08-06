import csv
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from core.models import AcademicYear, School
from people.models import Student
from .models import Expense, ExpenseCategory, Income, Invoice, InvoiceItem, Product, Transaction


# ==========================================
# EXPENSE CATEGORY VIEWS
# ==========================================

def _generate_expense_category_id():
    numbers = []
    for cat in ExpenseCategory.objects.exclude(category_id=""):
        if cat.category_id and cat.category_id.startswith("EXC") and cat.category_id[3:].isdigit():
            numbers.append(int(cat.category_id[3:]))
    candidate = max(numbers) + 1 if numbers else 617453
    while ExpenseCategory.objects.filter(category_id=f"EXC{candidate}").exists():
        candidate += 1
    return f"EXC{candidate}"


def expenses_category_next_id(request):
    return JsonResponse({"next_id": _generate_expense_category_id()})


def expenses_category_list(request):
    if request.method == "POST":
        if "add_category" in request.POST or "name" in request.POST and "edit_category" not in request.POST:
            posted_id = request.POST.get("category_id", "").strip()
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()
            if name:
                cat = ExpenseCategory(name=name, description=description)
                if posted_id:
                    cat.category_id = posted_id
                cat.save()
                messages.success(request, "Expense Category added successfully.")
            else:
                messages.error(request, "Category name is required.")
            return redirect("finance:expenses-category")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                ExpenseCategory.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} category(ies) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("finance:expenses-category")

    categories = ExpenseCategory.objects.all()

    filter_category = request.GET.get("filter_category", "").strip()
    if filter_category:
        categories = categories.filter(name=filter_category)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        categories = categories.order_by("-name")
    elif sort == "recent":
        categories = categories.order_by("-updated_at")
    elif sort == "recent_added":
        categories = categories.order_by("-created_at")
    else:
        categories = categories.order_by("name")

    category_names = ExpenseCategory.objects.values_list("name", flat=True).distinct().order_by("name")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/expenses-category.html", {
        "categories": categories,
        "category_names": category_names,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_category_id": _generate_expense_category_id(),
        "sort": sort,
        "filter_category": filter_category,
    })


def expenses_category_edit(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    if request.method == "POST":
        posted_id = request.POST.get("category_id", "").strip()
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            if posted_id:
                category.category_id = posted_id
            category.name = name
            category.description = description
            category.save()
            messages.success(request, "Expense Category updated successfully.")
        else:
            messages.error(request, "Category name is required.")
    return redirect("finance:expenses-category")


def expenses_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Expense Category deleted successfully.")
    return redirect("finance:expenses-category")


def expenses_category_export_excel(request):
    categories = ExpenseCategory.objects.all()
    filter_category = request.GET.get("filter_category", "").strip()
    if filter_category:
        categories = categories.filter(name=filter_category)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        categories = categories.order_by("-name")
    else:
        categories = categories.order_by("name")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="expense_categories.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Category", "Description"])

    for cat in categories:
        writer.writerow([cat.category_id, cat.name, cat.description])

    return response


def expenses_category_export_pdf(request):
    categories = ExpenseCategory.objects.all()
    filter_category = request.GET.get("filter_category", "").strip()
    if filter_category:
        categories = categories.filter(name=filter_category)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        categories = categories.order_by("-name")
    else:
        categories = categories.order_by("name")

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/expenses-category-print.html", {
        "categories": categories,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "title": "Expense Category Report",
    })


# ==========================================
# INCOME VIEWS
# ==========================================

def _generate_income_id():
    numbers = []
    for inc in Income.objects.exclude(income_id=""):
        if inc.income_id and inc.income_id.startswith("I") and inc.income_id[1:].isdigit():
            numbers.append(int(inc.income_id[1:]))
    candidate = max(numbers) + 1 if numbers else 639248
    while Income.objects.filter(income_id=f"I{candidate}").exists():
        candidate += 1
    return f"I{candidate}"


def _generate_income_invoice_number():
    numbers = []
    for inc in Income.objects.exclude(invoice_number=""):
        if inc.invoice_number and inc.invoice_number.startswith("INV") and inc.invoice_number[3:].isdigit():
            numbers.append(int(inc.invoice_number[3:]))
    candidate = max(numbers) + 1 if numbers else 681537
    while Income.objects.filter(invoice_number=f"INV{candidate}").exists():
        candidate += 1
    return f"INV{candidate}"


def _parse_income_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_income_amount(value):
    if not value:
        return None
    try:
        return Decimal(str(value).replace("$", "").replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _incomes_queryset():
    return Income.objects.all()


def _apply_income_filters(request, incomes):
    filter_income = request.GET.get("filter_income", "").strip()
    filter_source = request.GET.get("filter_source", "").strip()
    filter_invoice = request.GET.get("filter_invoice", "").strip()

    if filter_income:
        incomes = incomes.filter(income_name__icontains=filter_income)
    if filter_source:
        incomes = incomes.filter(source=filter_source)
    if filter_invoice:
        incomes = incomes.filter(invoice_number__icontains=filter_invoice)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        incomes = incomes.order_by("-income_name")
    elif sort == "recent":
        incomes = incomes.order_by("-updated_at")
    elif sort == "recent_added":
        incomes = incomes.order_by("-created_at")
    else:
        incomes = incomes.order_by("income_name")
    return incomes, filter_income, filter_source, filter_invoice, sort


def incomes_next_id(request):
    return JsonResponse({
        "next_id": _generate_income_id(),
        "next_invoice": _generate_income_invoice_number(),
    })


def incomes_list(request):
    if request.method == "POST":
        if "add_income" in request.POST:
            income_name = request.POST.get("income_name", "").strip()
            amount = _parse_income_amount(request.POST.get("amount", ""))
            income_date = _parse_income_date(request.POST.get("date", ""))
            if income_name and amount is not None and income_date:
                income = Income(
                    income_name=income_name,
                    amount=amount,
                    date=income_date,
                    description=request.POST.get("description", "").strip(),
                    source=request.POST.get("source", "other") or "other",
                    payment_method=request.POST.get("payment_method", "cash") or "cash",
                )
                income_id = request.POST.get("income_id", "").strip()
                if income_id:
                    if Income.objects.filter(income_id=income_id).exists():
                        income.income_id = _generate_income_id()
                    else:
                        income.income_id = income_id
                invoice_number = request.POST.get("invoice_number", "").strip()
                if invoice_number:
                    if Income.objects.filter(invoice_number=invoice_number).exists():
                        income.invoice_number = _generate_income_invoice_number()
                    else:
                        income.invoice_number = invoice_number
                income.save()
                messages.success(request, "Income added successfully.")
            else:
                messages.error(request, "Income name, amount and date are required.")
            return redirect("finance:incomes")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Income.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} income(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("finance:incomes")

    incomes, filter_income, filter_source, filter_invoice, sort = _apply_income_filters(
        request, _incomes_queryset()
    )

    income_names = Income.objects.values_list("income_name", flat=True).distinct().order_by("income_name")
    source_names = [{"value": value, "label": label} for value, label in Income.SOURCE_CHOICES]
    invoice_numbers = Income.objects.values_list("invoice_number", flat=True).distinct().order_by("-invoice_number")
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/accounts-income.html", {
        "incomes": incomes,
        "income_names": income_names,
        "source_names": source_names,
        "invoice_numbers": invoice_numbers,
        "payment_methods": Income.PAYMENT_METHOD_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_income_id": _generate_income_id(),
        "next_invoice_number": _generate_income_invoice_number(),
        "sort": sort,
        "filter_income": filter_income,
        "filter_source": filter_source,
        "filter_invoice": filter_invoice,
    })


def incomes_edit(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == "POST":
        income_name = request.POST.get("income_name", "").strip()
        amount = _parse_income_amount(request.POST.get("amount", ""))
        income_date = _parse_income_date(request.POST.get("date", ""))
        if income_name and amount is not None and income_date:
            income.income_name = income_name
            income.amount = amount
            income.date = income_date
            income.description = request.POST.get("description", "").strip()
            income.source = request.POST.get("source", "other") or "other"
            income.payment_method = request.POST.get("payment_method", "cash") or "cash"
            income_id = request.POST.get("income_id", "").strip()
            if income_id:
                if Income.objects.filter(income_id=income_id).exclude(pk=income.pk).exists():
                    income.income_id = _generate_income_id()
                else:
                    income.income_id = income_id
            invoice_number = request.POST.get("invoice_number", "").strip()
            if invoice_number:
                if Income.objects.filter(invoice_number=invoice_number).exclude(pk=income.pk).exists():
                    income.invoice_number = _generate_income_invoice_number()
                else:
                    income.invoice_number = invoice_number
            income.save()
            messages.success(request, "Income updated successfully.")
        else:
            messages.error(request, "Income name, amount and date are required.")
    return redirect("finance:incomes")


def incomes_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == "POST":
        income.delete()
        messages.success(request, "Income deleted successfully.")
    return redirect("finance:incomes")


def incomes_export_excel(request):
    incomes, filter_income, filter_source, filter_invoice, sort = _apply_income_filters(
        request, _incomes_queryset()
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="incomes.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Income Name", "Description", "Source", "Date", "Amount", "Invoice No", "Payment Method"])

    for inc in incomes:
        writer.writerow([
            inc.income_id,
            inc.income_name,
            inc.description,
            inc.get_source_display(),
            inc.date.strftime("%d %b %Y"),
            inc.amount_display,
            inc.invoice_number,
            inc.get_payment_method_display(),
        ])

    return response


def incomes_export_pdf(request):
    incomes, filter_income, filter_source, filter_invoice, sort = _apply_income_filters(
        request, _incomes_queryset()
    )

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/accounts-income-print.html", {
        "incomes": incomes,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "title": "Income Report",
    })


# ==========================================
# EXPENSE VIEWS
# ==========================================

def _generate_expense_id():
    numbers = []
    for exp in Expense.objects.exclude(expense_id=""):
        if exp.expense_id and exp.expense_id.startswith("EX") and exp.expense_id[2:].isdigit():
            numbers.append(int(exp.expense_id[2:]))
    candidate = max(numbers) + 1 if numbers else 628148
    while Expense.objects.filter(expense_id=f"EX{candidate}").exists():
        candidate += 1
    return f"EX{candidate}"


def _generate_invoice_number():
    numbers = []
    for exp in Expense.objects.exclude(invoice_number=""):
        if exp.invoice_number and exp.invoice_number.startswith("INV") and exp.invoice_number[3:].isdigit():
            numbers.append(int(exp.invoice_number[3:]))
    candidate = max(numbers) + 1 if numbers else 681537
    while Expense.objects.filter(invoice_number=f"INV{candidate}").exists():
        candidate += 1
    return f"INV{candidate}"


def _resolve_expense_id(posted_id, exclude_pk=None):
    posted_id = (posted_id or "").strip()
    queryset = Expense.objects.all()
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    if posted_id and not queryset.filter(expense_id=posted_id).exists():
        return posted_id
    return _generate_expense_id()


def _parse_expense_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_expense_amount(value):
    if not value:
        return None
    try:
        return Decimal(str(value).replace("$", "").replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _expenses_queryset():
    return Expense.objects.all().select_related("category")


def _apply_expense_filters(request, expenses):
    filter_expense = request.GET.get("filter_expense", "").strip()
    filter_category = request.GET.get("filter_category", "").strip()
    filter_invoice = request.GET.get("filter_invoice", "").strip()

    if filter_expense:
        expenses = expenses.filter(expense_name__icontains=filter_expense)
    if filter_category:
        expenses = expenses.filter(category__name=filter_category)
    if filter_invoice:
        expenses = expenses.filter(invoice_number__icontains=filter_invoice)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        expenses = expenses.order_by("-expense_name")
    elif sort == "recent":
        expenses = expenses.order_by("-updated_at")
    elif sort == "recent_added":
        expenses = expenses.order_by("-created_at")
    else:
        expenses = expenses.order_by("expense_name")
    return expenses, filter_expense, filter_category, filter_invoice, sort


def expenses_next_id(request):
    return JsonResponse({
        "next_id": _generate_expense_id(),
        "next_invoice": _generate_invoice_number(),
    })


def expenses_list(request):
    if request.method == "POST":
        if "add_expense" in request.POST:
            expense_name = request.POST.get("expense_name", "").strip()
            amount = _parse_expense_amount(request.POST.get("amount", ""))
            expense_date = _parse_expense_date(request.POST.get("date", ""))
            if expense_name and amount is not None and expense_date:
                expense = Expense(
                    expense_name=expense_name,
                    amount=amount,
                    date=expense_date,
                    description=request.POST.get("description", "").strip(),
                    payment_method=request.POST.get("payment_method", "cash") or "cash",
                    status=request.POST.get("status", "paid") or "paid",
                    expense_id=_resolve_expense_id(request.POST.get("expense_id", "")),
                )
                category_id = request.POST.get("category", "").strip()
                if category_id:
                    expense.category = ExpenseCategory.objects.filter(pk=category_id).first()
                invoice_number = request.POST.get("invoice_number", "").strip()
                if invoice_number:
                    if Expense.objects.filter(invoice_number=invoice_number).exists():
                        expense.invoice_number = _generate_invoice_number()
                    else:
                        expense.invoice_number = invoice_number
                expense.save()
                messages.success(request, "Expense added successfully.")
            else:
                messages.error(request, "Expense name, amount and date are required.")
            return redirect("finance:expenses")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Expense.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} expense(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("finance:expenses")

    expenses, filter_expense, filter_category, filter_invoice, sort = _apply_expense_filters(
        request, _expenses_queryset()
    )

    expense_names = Expense.objects.values_list("expense_name", flat=True).distinct().order_by("expense_name")
    category_names = ExpenseCategory.objects.values_list("name", flat=True).distinct().order_by("name")
    invoice_numbers = Expense.objects.values_list("invoice_number", flat=True).distinct().order_by("-invoice_number")
    categories = ExpenseCategory.objects.all()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/expenses.html", {
        "expenses": expenses,
        "categories": categories,
        "expense_names": expense_names,
        "category_names": category_names,
        "invoice_numbers": invoice_numbers,
        "payment_methods": Expense.PAYMENT_METHOD_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_expense_id": _generate_expense_id(),
        "next_invoice_number": _generate_invoice_number(),
        "sort": sort,
        "filter_expense": filter_expense,
        "filter_category": filter_category,
        "filter_invoice": filter_invoice,
    })


def expenses_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        expense_name = request.POST.get("expense_name", "").strip()
        amount = _parse_expense_amount(request.POST.get("amount", ""))
        expense_date = _parse_expense_date(request.POST.get("date", ""))
        if expense_name and amount is not None and expense_date:
            expense.expense_name = expense_name
            expense.expense_id = _resolve_expense_id(request.POST.get("expense_id", ""), exclude_pk=expense.pk)
            expense.amount = amount
            expense.date = expense_date
            expense.description = request.POST.get("description", "").strip()
            expense.payment_method = request.POST.get("payment_method", "cash") or "cash"
            expense.status = request.POST.get("status", "paid") or "paid"
            category_id = request.POST.get("category", "").strip()
            expense.category = ExpenseCategory.objects.filter(pk=category_id).first() if category_id else None
            invoice_number = request.POST.get("invoice_number", "").strip()
            if invoice_number:
                if Expense.objects.filter(invoice_number=invoice_number).exclude(pk=expense.pk).exists():
                    expense.invoice_number = _generate_invoice_number()
                else:
                    expense.invoice_number = invoice_number
            expense.save()
            messages.success(request, "Expense updated successfully.")
        else:
            messages.error(request, "Expense name, amount and date are required.")
    return redirect("finance:expenses")


def expenses_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully.")
    return redirect("finance:expenses")


def expenses_export_excel(request):
    expenses, filter_expense, filter_category, filter_invoice, sort = _apply_expense_filters(
        request, _expenses_queryset()
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="expenses.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Expense Name", "Description", "Category", "Date", "Amount", "Invoice No", "Payment Method"])

    for exp in expenses:
        writer.writerow([
            exp.expense_id,
            exp.expense_name,
            exp.description,
            exp.category.name if exp.category else "",
            exp.date.strftime("%d %b %Y"),
            exp.amount_display,
            exp.invoice_number,
            exp.get_payment_method_display(),
        ])

    return response


def expenses_export_pdf(request):
    expenses, filter_expense, filter_category, filter_invoice, sort = _apply_expense_filters(
        request, _expenses_queryset()
    )

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/expenses-print.html", {
        "expenses": expenses,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "title": "Expense Report",
    })


# ==========================================
# INVOICE VIEWS
# ==========================================

def _generate_invoice_number():
    numbers = []
    for inv in Invoice.objects.exclude(invoice_number=""):
        if inv.invoice_number and inv.invoice_number.startswith("INV") and inv.invoice_number[3:].isdigit():
            numbers.append(int(inv.invoice_number[3:]))
    candidate = max(numbers) + 1 if numbers else 681537
    while Invoice.objects.filter(invoice_number=f"INV{candidate}").exists():
        candidate += 1
    return f"INV{candidate}"


def _parse_invoice_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_invoice_amount(value):
    return _parse_income_amount(value)


def _parse_invoice_percent(value):
    if not value:
        return Decimal("0")
    try:
        return Decimal(str(value).replace("%", "").strip())
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _parse_invoice_quantity(value):
    if not value:
        return Decimal("1")
    try:
        qty = Decimal(str(value).strip())
        return qty if qty > 0 else Decimal("1")
    except (InvalidOperation, ValueError):
        return Decimal("1")


def _parse_invoice_items(request):
    items = []
    descriptions = request.POST.getlist("item_description")
    quantities = request.POST.getlist("item_quantity")
    unit_prices = request.POST.getlist("item_unit_price")
    discounts = request.POST.getlist("item_discount")
    for i, desc in enumerate(descriptions):
        desc = (desc or "").strip()
        qty = _parse_invoice_quantity(quantities[i]) if i < len(quantities) else Decimal("1")
        price = _parse_invoice_amount(unit_prices[i]) if i < len(unit_prices) else Decimal("0")
        disc = _parse_invoice_percent(discounts[i]) if i < len(discounts) else Decimal("0")
        if desc or price:
            net = qty * price
            if disc:
                net = net * (Decimal("1") - disc / Decimal("100"))
            items.append({
                "description": desc or "Item",
                "quantity": int(qty),
                "unit_price": price,
                "discount_percent": disc,
                "amount": net.quantize(Decimal("0.01")),
            })
    return items


def _invoices_queryset():
    return Invoice.objects.all().prefetch_related("items")


def _apply_invoice_filters(request, invoices):
    filter_invoice = request.GET.get("filter_invoice", "").strip()
    filter_date = request.GET.get("filter_date", "").strip()
    filter_payment = request.GET.get("filter_payment", "").strip()

    if filter_invoice:
        invoices = invoices.filter(invoice_number__icontains=filter_invoice)
    if filter_date:
        parsed_date = _parse_invoice_date(filter_date)
        if parsed_date:
            invoices = invoices.filter(date=parsed_date)
    if filter_payment:
        invoices = invoices.filter(payment_method=filter_payment)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        invoices = invoices.order_by("-invoice_number")
    elif sort == "recent":
        invoices = invoices.order_by("-updated_at")
    elif sort == "recent_added":
        invoices = invoices.order_by("-created_at")
    else:
        invoices = invoices.order_by("invoice_number")
    return invoices, filter_invoice, filter_date, filter_payment, sort


def invoices_next_id(request):
    return JsonResponse({"next_invoice": _generate_invoice_number()})


def invoices_list(request):
    if request.method == "POST":
        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Invoice.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} invoice(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("finance:invoices")

    invoices, filter_invoice, filter_date, filter_payment, sort = _apply_invoice_filters(
        request, _invoices_queryset()
    )

    invoice_numbers = Invoice.objects.values_list("invoice_number", flat=True).distinct().order_by("-invoice_number")
    invoice_dates = [d.strftime("%d %b %Y") for d in Invoice.objects.values_list("date", flat=True).distinct().order_by("-date")]
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/accounts-invoices.html", {
        "invoices": invoices,
        "invoice_numbers": invoice_numbers,
        "invoice_dates": invoice_dates,
        "payment_methods": Invoice.PAYMENT_METHOD_CHOICES,
        "statuses": Invoice.STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_invoice_number": _generate_invoice_number(),
        "sort": sort,
        "filter_invoice": filter_invoice,
        "filter_date": filter_date,
        "filter_payment": filter_payment,
    })


def _products_context():
    products = Product.objects.filter(is_active=True)
    products_json = json.dumps([
        {
            "id": product.pk,
            "name": product.name,
            "price": float(product.unit_price),
        }
        for product in products
    ])
    return products, products_json


def _students_context():
    return Student.objects.filter(status="active").order_by("name")


def _resolve_customer(request):
    student_name = ""
    student_id = ""
    customer_pk = request.POST.get("customer", "").strip()
    if customer_pk:
        student = Student.objects.filter(pk=customer_pk).first()
        if student:
            student_name = student.name
            student_id = student.admission_no
    else:
        student_name = request.POST.get("student_name", "").strip()
        student_id = request.POST.get("student_id", "").strip()
    return student_name, student_id


def add_invoice_page(request):
    if request.method == "POST":
        invoice_number = request.POST.get("invoice_number", "").strip()
        invoice_date = _parse_invoice_date(request.POST.get("date", ""))
        due_date = _parse_invoice_date(request.POST.get("due_date", ""))
        items_data = _parse_invoice_items(request)
        subtotal = sum((item_data["amount"] for item_data in items_data), Decimal("0"))
        if not invoice_number:
            invoice_number = _generate_invoice_number()
        if invoice_number and invoice_date and items_data:
            if Invoice.objects.filter(invoice_number=invoice_number).exists():
                invoice_number = _generate_invoice_number()
            student_name, student_id = _resolve_customer(request)
            description = ", ".join(item_data["description"] for item_data in items_data)
            invoice = Invoice(
                invoice_number=invoice_number,
                student_name=student_name,
                student_id=student_id,
                description=description[:400],
                bill_to_address=request.POST.get("bill_to_address", "").strip(),
                bill_to_email=request.POST.get("bill_to_email", "").strip(),
                bill_to_phone=request.POST.get("bill_to_phone", "").strip(),
                date=invoice_date,
                due_date=due_date,
                amount=subtotal,
                discount=_parse_invoice_percent(request.POST.get("discount", "")),
                tax=_parse_invoice_percent(request.POST.get("tax", "")),
                payment_method=request.POST.get("payment_method", "cash") or "cash",
                status=request.POST.get("status", "pending") or "pending",
                terms=request.POST.get("terms", "").strip(),
                notes=request.POST.get("notes", "").strip(),
                signature_name=request.POST.get("signature_name", "").strip(),
            )
            if request.FILES.get("company_logo"):
                invoice.company_logo = request.FILES.get("company_logo")
            if request.FILES.get("signature"):
                invoice.signature = request.FILES.get("signature")
            invoice.save()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=invoice, **item_data)
            messages.success(request, "Invoice added successfully.")
            return redirect("finance:invoices")
        messages.error(request, "Invoice number, date and at least one product line are required.")
        return redirect("finance:invoices-add")

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()
    products, products_json = _products_context()

    return render(request, "portaluser/finance/add-invoice.html", {
        "next_invoice_number": _generate_invoice_number(),
        "students": _students_context(),
        "products": products,
        "products_json": products_json,
        "payment_methods": Invoice.PAYMENT_METHOD_CHOICES,
        "statuses": Invoice.STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def edit_invoice_page(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        invoice_number = request.POST.get("invoice_number", "").strip()
        invoice_date = _parse_invoice_date(request.POST.get("date", ""))
        due_date = _parse_invoice_date(request.POST.get("due_date", ""))
        items_data = _parse_invoice_items(request)
        subtotal = sum((item_data["amount"] for item_data in items_data), Decimal("0"))
        if invoice_number and invoice_date and items_data:
            if Invoice.objects.filter(invoice_number=invoice_number).exclude(pk=invoice.pk).exists():
                invoice_number = _generate_invoice_number()
            student_name, student_id = _resolve_customer(request)
            description = ", ".join(item_data["description"] for item_data in items_data)
            invoice.invoice_number = invoice_number
            invoice.student_name = student_name
            invoice.student_id = student_id
            invoice.description = description[:400]
            invoice.bill_to_address = request.POST.get("bill_to_address", "").strip()
            invoice.bill_to_email = request.POST.get("bill_to_email", "").strip()
            invoice.bill_to_phone = request.POST.get("bill_to_phone", "").strip()
            invoice.date = invoice_date
            invoice.due_date = due_date
            invoice.amount = subtotal
            invoice.discount = _parse_invoice_percent(request.POST.get("discount", ""))
            invoice.tax = _parse_invoice_percent(request.POST.get("tax", ""))
            invoice.payment_method = request.POST.get("payment_method", "cash") or "cash"
            invoice.status = request.POST.get("status", "pending") or "pending"
            invoice.terms = request.POST.get("terms", "").strip()
            invoice.notes = request.POST.get("notes", "").strip()
            invoice.signature_name = request.POST.get("signature_name", "").strip()
            if request.FILES.get("company_logo"):
                invoice.company_logo = request.FILES.get("company_logo")
            if request.FILES.get("signature"):
                invoice.signature = request.FILES.get("signature")
            invoice.save()
            invoice.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=invoice, **item_data)
            messages.success(request, "Invoice updated successfully.")
            return redirect("finance:invoices")
        messages.error(request, "Invoice number, date and at least one product line are required.")

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()
    products, products_json = _products_context()

    return render(request, "portaluser/finance/edit-invoice.html", {
        "invoice": invoice,
        "students": _students_context(),
        "products": products,
        "products_json": products_json,
        "payment_methods": Invoice.PAYMENT_METHOD_CHOICES,
        "statuses": Invoice.STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def invoices_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        invoice.delete()
        messages.success(request, "Invoice deleted successfully.")
    return redirect("finance:invoices")


def invoice_view(request, pk):
    invoice = get_object_or_404(_invoices_queryset(), pk=pk)
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/invoice.html", {
        "invoice": invoice,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
    })


def invoice_view_latest(request):
    invoice = _invoices_queryset().first()
    if invoice:
        return redirect("finance:invoice-view", pk=invoice.pk)
    messages.info(request, "No invoices found yet.")
    return redirect("finance:invoices")


def invoices_export_excel(request):
    invoices, filter_invoice, filter_date, filter_payment, sort = _apply_invoice_filters(
        request, _invoices_queryset()
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="invoices.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["Invoice Number", "Student Name", "Student ID", "Term", "Description", "Date", "Due Date", "Amount", "Payment Method", "Status"])

    for inv in invoices:
        writer.writerow([
            inv.invoice_number,
            inv.student_name,
            inv.student_id,
            inv.term,
            inv.description,
            inv.date.strftime("%d %b %Y"),
            inv.due_date.strftime("%d %b %Y") if inv.due_date else "",
            inv.amount_display,
            inv.get_payment_method_display(),
            inv.get_status_display(),
        ])

    return response


def invoices_export_pdf(request):
    invoices, filter_invoice, filter_date, filter_payment, sort = _apply_invoice_filters(
        request, _invoices_queryset()
    )

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/accounts-invoices-print.html", {
        "invoices": invoices,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "title": "Invoice Report",
    })


# ==========================================
# TRANSACTION VIEWS
# ==========================================

def _generate_transaction_id():
    numbers = []
    for txn in Transaction.objects.exclude(transaction_id=""):
        if txn.transaction_id and txn.transaction_id.startswith("FT") and txn.transaction_id[2:].isdigit():
            numbers.append(int(txn.transaction_id[2:]))
    candidate = max(numbers) + 1 if numbers else 624893
    while Transaction.objects.filter(transaction_id=f"FT{candidate}").exists():
        candidate += 1
    return f"FT{candidate}"


def _parse_transaction_date(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_transaction_amount(value):
    if not value:
        return None
    try:
        return Decimal(str(value).replace("$", "").replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _transactions_queryset():
    return Transaction.objects.all()


def _apply_transaction_filters(request, transactions):
    filter_transaction = request.GET.get("filter_transaction", "").strip()
    filter_type = request.GET.get("filter_type", "").strip()
    filter_date = request.GET.get("filter_date", "").strip()

    if filter_transaction:
        transactions = transactions.filter(transaction_id__icontains=filter_transaction)
    if filter_type:
        transactions = transactions.filter(transaction_type=filter_type)
    if filter_date:
        parsed_date = _parse_transaction_date(filter_date)
        if parsed_date:
            transactions = transactions.filter(date=parsed_date)

    sort = request.GET.get("sort", "asc")
    if sort == "desc":
        transactions = transactions.order_by("-description")
    elif sort == "recent":
        transactions = transactions.order_by("-updated_at")
    elif sort == "recent_added":
        transactions = transactions.order_by("-created_at")
    else:
        transactions = transactions.order_by("description")
    return transactions, filter_transaction, filter_type, filter_date, sort


def transactions_next_id(request):
    return JsonResponse({"next_id": _generate_transaction_id()})


def transactions_list(request):
    if request.method == "POST":
        if "add_transaction" in request.POST:
            description = request.POST.get("description", "").strip()
            amount = _parse_transaction_amount(request.POST.get("amount", ""))
            txn_date = _parse_transaction_date(request.POST.get("date", ""))
            if description and amount is not None and txn_date:
                txn = Transaction(
                    description=description,
                    amount=amount,
                    date=txn_date,
                    transaction_type=request.POST.get("transaction_type", "income") or "income",
                    payment_method=request.POST.get("payment_method", "cash") or "cash",
                    status=request.POST.get("status", "completed") or "completed",
                )
                txn_id = request.POST.get("transaction_id", "").strip()
                if txn_id:
                    if Transaction.objects.filter(transaction_id=txn_id).exists():
                        txn.transaction_id = _generate_transaction_id()
                    else:
                        txn.transaction_id = txn_id
                txn.save()
                messages.success(request, "Transaction added successfully.")
            else:
                messages.error(request, "Description, amount and date are required.")
            return redirect("finance:transactions")

        if "bulk_delete" in request.POST:
            ids = request.POST.getlist("selected_items")
            if ids:
                Transaction.objects.filter(pk__in=ids).delete()
                messages.success(request, f"{len(ids)} transaction(s) deleted successfully.")
            else:
                messages.warning(request, "No items selected for deletion.")
            return redirect("finance:transactions")

    transactions, filter_transaction, filter_type, filter_date, sort = _apply_transaction_filters(
        request, _transactions_queryset()
    )

    transaction_ids = Transaction.objects.values_list("transaction_id", flat=True).distinct().order_by("-transaction_id")
    transaction_dates = [d.strftime("%d %b %Y") for d in Transaction.objects.values_list("date", flat=True).distinct().order_by("-date")]
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/accounts-transactions.html", {
        "transactions": transactions,
        "transaction_ids": transaction_ids,
        "transaction_dates": transaction_dates,
        "transaction_types": Transaction.TRANSACTION_TYPE_CHOICES,
        "payment_methods": Transaction.PAYMENT_METHOD_CHOICES,
        "statuses": Transaction.STATUS_CHOICES,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "next_transaction_id": _generate_transaction_id(),
        "sort": sort,
        "filter_transaction": filter_transaction,
        "filter_type": filter_type,
        "filter_date": filter_date,
    })


def transactions_edit(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        description = request.POST.get("description", "").strip()
        amount = _parse_transaction_amount(request.POST.get("amount", ""))
        txn_date = _parse_transaction_date(request.POST.get("date", ""))
        if description and amount is not None and txn_date:
            txn.description = description
            txn.amount = amount
            txn.date = txn_date
            txn.transaction_type = request.POST.get("transaction_type", "income") or "income"
            txn.payment_method = request.POST.get("payment_method", "cash") or "cash"
            txn.status = request.POST.get("status", "completed") or "completed"
            txn_id = request.POST.get("transaction_id", "").strip()
            if txn_id:
                if Transaction.objects.filter(transaction_id=txn_id).exclude(pk=txn.pk).exists():
                    txn.transaction_id = _generate_transaction_id()
                else:
                    txn.transaction_id = txn_id
            txn.save()
            messages.success(request, "Transaction updated successfully.")
        else:
            messages.error(request, "Description, amount and date are required.")
    return redirect("finance:transactions")


def transactions_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        txn.delete()
        messages.success(request, "Transaction deleted successfully.")
    return redirect("finance:transactions")


def transactions_export_excel(request):
    transactions, filter_transaction, filter_type, filter_date, sort = _apply_transaction_filters(
        request, _transactions_queryset()
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Description", "Transaction Date", "Amount", "Transaction Type", "Payment Method", "Status"])

    for txn in transactions:
        writer.writerow([
            txn.transaction_id,
            txn.description,
            txn.date.strftime("%d %b %Y"),
            txn.amount_display,
            txn.get_transaction_type_display(),
            txn.get_payment_method_display(),
            txn.get_status_display(),
        ])

    return response


def transactions_export_pdf(request):
    transactions, filter_transaction, filter_type, filter_date, sort = _apply_transaction_filters(
        request, _transactions_queryset()
    )

    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/finance/accounts-transactions-print.html", {
        "transactions": transactions,
        "current_academic_year": current_academic_year,
        "school_name": school.name if school else "Global International",
        "title": "Transaction Report",
    })
