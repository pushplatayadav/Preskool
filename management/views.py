import csv
import random
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from core.models import AcademicYear, School
from .models import LibraryMember, Book, BookIssue, BookReturn, Sport, Player, Hostel, HostelRoom, HostelRoomType, TransportRoute, TransportPickupPoint, TransportVehicleDriver, TransportVehicle, TransportAssignVehicle


# ==========================================
# LIBRARY MEMBERS VIEWS
# ==========================================

def _get_next_member_id():
    for _ in range(100):
        candidate = f"LM823{random.randint(700, 999)}"
        if not LibraryMember.objects.filter(member_id=candidate).exists():
            return candidate
    return f"LM{random.randint(100000, 999999)}"


def _get_next_card_no():
    existing_cards = LibraryMember.objects.values_list('card_no', flat=True)
    numeric_cards = []
    for c in existing_cards:
        try:
            numeric_cards.append(int(c))
        except ValueError:
            pass
    if numeric_cards:
        return str(max(numeric_cards) + 1)
    return "501"


def _parse_date(value):
    value = (value or "").strip()
    if not value:
        return date.today()

    formats = (
        "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
        "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
        "%Y/%m/%d", "%d.%m.%Y", "%Y.%m.%d"
    )
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    try:
        parts = value.replace('/', '-').replace('.', '-').split('-')
        if len(parts) == 3:
            p1, p2, p3 = int(parts[0]), int(parts[1]), int(parts[2])
            if p1 > 1000:
                return date(p1, p2, p3)
            elif p3 > 1000:
                return date(p3, p2, p1)
    except Exception:
        pass

    return date.today()


def library_members_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_member" in request.POST:
            member_id = request.POST.get("member_id", "").strip()
            card_no = request.POST.get("card_no", "").strip()
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            mobile = request.POST.get("mobile", "").strip()
            raw_date = request.POST.get("date_of_join", "")
            date_of_join = _parse_date(raw_date)
            status = request.POST.get("status", "Active")

            if not member_id or LibraryMember.objects.filter(member_id=member_id).exists():
                member_id = _get_next_member_id()

            if not card_no:
                card_no = _get_next_card_no()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Member Name is required."})
                messages.error(request, "Member Name is required.")
                return redirect("management:library-members")

            if LibraryMember.objects.filter(card_no=card_no).exists():
                card_no = _get_next_card_no()

            member = LibraryMember.objects.create(
                member_id=member_id,
                card_no=card_no,
                name=name,
                email=email,
                mobile=mobile,
                date_of_join=date_of_join,
                status=status,
            )
            if request.FILES.get("avatar"):
                member.avatar = request.FILES["avatar"]
                member.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Library member added successfully."})
            messages.success(request, f"Library member '{name}' (ID: {member_id}, Card No: {card_no}) added successfully.")
            return redirect("management:library-members")

        if "edit_member" in request.POST:
            member = get_object_or_404(LibraryMember, pk=request.POST.get("member_db_id"))
            member_id_val = request.POST.get("member_id_val", "").strip()
            card_no = request.POST.get("card_no", "").strip()
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            mobile = request.POST.get("mobile", "").strip()
            raw_date = request.POST.get("date_of_join", "")
            date_of_join = _parse_date(raw_date)
            status = request.POST.get("status", "Active")

            if not card_no:
                card_no = member.card_no

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Member Name is required."})
                messages.error(request, "Member Name is required.")
                return redirect("management:library-members")

            if LibraryMember.objects.filter(card_no=card_no).exclude(pk=member.pk).exists():
                card_no = _get_next_card_no()

            if member_id_val:
                member.member_id = member_id_val
            member.card_no = card_no
            member.name = name
            member.email = email
            member.mobile = mobile
            member.date_of_join = date_of_join
            member.status = status
            if request.FILES.get("avatar"):
                member.avatar = request.FILES["avatar"]
            member.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Library member updated successfully."})
            messages.success(request, f"Library member '{name}' updated successfully.")
            return redirect("management:library-members")

        if "delete_member" in request.POST:
            member = get_object_or_404(LibraryMember, pk=request.POST.get("member_db_id"))
            member_name = member.name
            member.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Library member deleted successfully."})
            messages.success(request, f"Library member '{member_name}' deleted successfully.")
            return redirect("management:library-members")

    members = LibraryMember.objects.all()

    filter_member = request.GET.get("filter_member", "").strip()
    filter_card = request.GET.get("filter_card", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_member:
        members = members.filter(name__icontains=filter_member)
    if filter_card:
        members = members.filter(card_no=filter_card)
    if filter_status in ("Active", "Inactive"):
        members = members.filter(status=filter_status)

    if sort_by == "name_desc":
        members = members.order_by("-name")
    elif sort_by == "date_asc":
        members = members.order_by("date_of_join")
    elif sort_by == "date_desc":
        members = members.order_by("-date_of_join")
    else:
        members = members.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_members = LibraryMember.objects.all()

    return render(request, "portaluser/management/library-members.html", {
        "members": members,
        "all_members": all_members,
        "filter_member": filter_member,
        "filter_card": filter_card,
        "filter_status": filter_status,
        "sort_by": sort_by,
        "next_member_id": _get_next_member_id(),
        "next_card_no": _get_next_card_no(),
        "today_date": date.today().strftime("%Y-%m-%d"),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def library_members_export_pdf(request):
    members = LibraryMember.objects.all().order_by("card_no")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/library-members-print.html", {
        "members": members,
        "school_name": school.name if school else "Global International",
        "title": "Library Members Report",
    })


def library_members_export_excel(request):
    members = LibraryMember.objects.all().order_by("card_no")

    filename = f"library_members_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Member", "Card No", "Email", "Date of Join", "Mobile", "Status"])

    for m in members:
        writer.writerow([
            m.member_id or "-",
            m.name,
            m.card_no,
            m.email or "-",
            m.date_of_join.strftime("%d %b %Y") if m.date_of_join else "-",
            m.mobile or "-",
            m.status,
        ])

    return response


# ==========================================
# BOOKS VIEWS
# ==========================================

def _get_next_book_id():
    for _ in range(100):
        candidate = f"LB86{random.randint(1000, 9999)}"
        if not Book.objects.filter(book_id=candidate).exists():
            return candidate
    return f"LB{random.randint(100000, 999999)}"


def _get_next_book_no():
    existing_nos = Book.objects.values_list('book_no', flat=True)
    numeric_nos = []
    for n in existing_nos:
        try:
            numeric_nos.append(int(n))
        except ValueError:
            pass
    if numeric_nos:
        return str(max(numeric_nos) + 1)
    return "501"


def library_books_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_book" in request.POST:
            book_id = request.POST.get("book_id", "").strip()
            name = request.POST.get("name", "").strip()
            book_no = request.POST.get("book_no", "").strip()
            publisher = request.POST.get("publisher", "").strip()
            author = request.POST.get("author", "").strip()
            subject = request.POST.get("subject", "").strip()
            rack_no = request.POST.get("rack_no", "").strip()
            qty = request.POST.get("qty", "1").strip()
            available = request.POST.get("available", "").strip()
            price = request.POST.get("price", "0.00").strip()
            raw_post_date = request.POST.get("post_date", "")

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Book Name is required."})
                messages.error(request, "Book Name is required.")
                return redirect("management:library-books")

            if not book_id or Book.objects.filter(book_id=book_id).exists():
                book_id = _get_next_book_id()

            if not book_no:
                book_no = _get_next_book_no()

            try:
                qty_val = max(1, int(qty))
            except ValueError:
                qty_val = 1

            try:
                avail_val = int(available) if available else qty_val
            except ValueError:
                avail_val = qty_val

            try:
                price_val = float(price) if price else 0.0
            except ValueError:
                price_val = 0.0

            post_date_val = _parse_date(raw_post_date)

            book = Book.objects.create(
                book_id=book_id,
                name=name,
                book_no=book_no,
                publisher=publisher,
                author=author,
                subject=subject,
                rack_no=rack_no,
                qty=qty_val,
                available=avail_val,
                price=price_val,
                post_date=post_date_val,
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Book added successfully."})
            messages.success(request, f"Book '{name}' (ID: {book_id}, No: {book_no}) added successfully.")
            return redirect("management:library-books")

        if "edit_book" in request.POST:
            book = get_object_or_404(Book, pk=request.POST.get("book_db_id"))
            name = request.POST.get("name", "").strip()
            book_no = request.POST.get("book_no", "").strip()
            publisher = request.POST.get("publisher", "").strip()
            author = request.POST.get("author", "").strip()
            subject = request.POST.get("subject", "").strip()
            rack_no = request.POST.get("rack_no", "").strip()
            qty = request.POST.get("qty", "1").strip()
            available = request.POST.get("available", "").strip()
            price = request.POST.get("price", "0.00").strip()
            raw_post_date = request.POST.get("post_date", "")

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Book Name is required."})
                messages.error(request, "Book Name is required.")
                return redirect("management:library-books")

            try:
                qty_val = max(1, int(qty))
            except ValueError:
                qty_val = book.qty

            try:
                avail_val = int(available) if available else qty_val
            except ValueError:
                avail_val = book.available

            try:
                price_val = float(price) if price else float(book.price)
            except ValueError:
                price_val = float(book.price)

            book.name = name
            if book_no:
                book.book_no = book_no
            book.publisher = publisher
            book.author = author
            book.subject = subject
            book.rack_no = rack_no
            book.qty = qty_val
            book.available = avail_val
            book.price = price_val
            book.post_date = _parse_date(raw_post_date)
            book.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Book updated successfully."})
            messages.success(request, f"Book '{name}' updated successfully.")
            return redirect("management:library-books")

        if "delete_book" in request.POST:
            book = get_object_or_404(Book, pk=request.POST.get("book_db_id"))
            book_name = book.name
            book.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Book deleted successfully."})
            messages.success(request, f"Book '{book_name}' deleted successfully.")
            return redirect("management:library-books")

    books = Book.objects.all()

    filter_subject = request.GET.get("filter_subject", "").strip()
    filter_book_no = request.GET.get("filter_book_no", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_subject:
        books = books.filter(subject__iexact=filter_subject)
    if filter_book_no:
        books = books.filter(book_no=filter_book_no)
    if search:
        books = books.filter(
            models.Q(name__icontains=search) |
            models.Q(book_id__icontains=search) |
            models.Q(author__icontains=search) |
            models.Q(publisher__icontains=search)
        )

    if sort_by == "name_desc":
        books = books.order_by("-name")
    elif sort_by == "date_asc":
        books = books.order_by("post_date")
    elif sort_by == "date_desc":
        books = books.order_by("-post_date")
    else:
        books = books.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_books = Book.objects.all()
    subjects = Book.objects.values_list('subject', flat=True).distinct()

    return render(request, "portaluser/management/library-books.html", {
        "books": books,
        "all_books": all_books,
        "subjects": [s for s in subjects if s],
        "filter_subject": filter_subject,
        "filter_book_no": filter_book_no,
        "search": search,
        "sort_by": sort_by,
        "next_book_id": _get_next_book_id(),
        "next_book_no": _get_next_book_no(),
        "today_date": date.today().strftime("%Y-%m-%d"),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def library_books_export_pdf(request):
    books = Book.objects.all().order_by("book_no")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/library-books-print.html", {
        "books": books,
        "school_name": school.name if school else "Global International",
        "title": "Library Books Report",
    })


def library_books_export_excel(request):
    books = Book.objects.all().order_by("book_no")

    filename = f"library_books_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Book Name", "Book No", "Publisher", "Author", "Subject", "Rack No", "Qty", "Available", "Price", "Post Date"])

    for b in books:
        writer.writerow([
            b.book_id,
            b.name,
            b.book_no,
            b.publisher or "-",
            b.author or "-",
            b.subject or "-",
            b.rack_no or "-",
            b.qty,
            b.available,
            f"{b.price:.2f}",
            b.post_date.strftime("%d %b %Y") if b.post_date else "-",
        ])

    return response


# ==========================================
# ISSUE BOOK VIEWS
# ==========================================

def _get_next_issue_id():
    for _ in range(100):
        candidate = f"IB853{random.randint(600, 999)}"
        if not BookIssue.objects.filter(issue_id=candidate).exists():
            return candidate
    return f"IB{random.randint(100000, 999999)}"


def library_issue_book_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_issue" in request.POST:
            issue_id = request.POST.get("issue_id", "").strip()
            member_id = request.POST.get("member_id", "").strip()
            book_id = request.POST.get("book_id", "").strip()
            raw_issue_date = request.POST.get("issue_date", "")
            raw_due_date = request.POST.get("due_date", "")
            books_issued_count = request.POST.get("books_issued_count", "1").strip()
            remarks = request.POST.get("remarks", "Book Issued").strip()

            if not issue_id or BookIssue.objects.filter(issue_id=issue_id).exists():
                issue_id = _get_next_issue_id()

            member = get_object_or_404(LibraryMember, pk=member_id)
            book = Book.objects.filter(pk=book_id).first() if book_id else None

            issue_date = _parse_date(raw_issue_date)
            due_date = _parse_date(raw_due_date) if raw_due_date else (issue_date + timedelta(days=30))

            try:
                issued_count = max(1, int(books_issued_count))
            except ValueError:
                issued_count = 1

            book_issue = BookIssue.objects.create(
                issue_id=issue_id,
                member=member,
                book=book,
                issue_date=issue_date,
                due_date=due_date,
                books_issued_count=issued_count,
                books_returned_count=0,
                remarks=remarks or "Book Issued",
                status="Issued",
            )

            if book and book.available >= issued_count:
                book.available -= issued_count
                book.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Book issued successfully."})
            messages.success(request, f"Book issued to '{member.name}' (Issue ID: {issue_id}) successfully.")
            return redirect("management:library-issue-book")

        if "edit_issue" in request.POST:
            issue = get_object_or_404(BookIssue, pk=request.POST.get("issue_db_id"))
            raw_issue_date = request.POST.get("issue_date", "")
            raw_due_date = request.POST.get("due_date", "")
            books_issued_count = request.POST.get("books_issued_count", "1").strip()
            books_returned_count = request.POST.get("books_returned_count", "0").strip()
            remarks = request.POST.get("remarks", "").strip()
            status = request.POST.get("status", "Issued").strip()

            if raw_issue_date:
                issue.issue_date = _parse_date(raw_issue_date)
            if raw_due_date:
                issue.due_date = _parse_date(raw_due_date)

            try:
                issue.books_issued_count = max(1, int(books_issued_count))
            except ValueError:
                pass

            try:
                issue.books_returned_count = max(0, int(books_returned_count))
            except ValueError:
                pass

            if remarks:
                issue.remarks = remarks
            if status in ("Issued", "Returned", "Overdue"):
                issue.status = status

            issue.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Book issue record updated successfully."})
            messages.success(request, f"Book issue record '{issue.issue_id}' updated successfully.")
            return redirect("management:library-issue-book")

        if "delete_issue" in request.POST:
            issue = get_object_or_404(BookIssue, pk=request.POST.get("issue_db_id"))
            issue_code = issue.issue_id
            issue.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Book issue record deleted successfully."})
            messages.success(request, f"Book issue record '{issue_code}' deleted successfully.")
            return redirect("management:library-issue-book")

    issues = BookIssue.objects.select_related("member", "book").all()

    filter_member = request.GET.get("filter_member", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_member:
        issues = issues.filter(member__name__icontains=filter_member)
    if filter_status in ("Issued", "Returned", "Overdue"):
        issues = issues.filter(status=filter_status)
    if search:
        issues = issues.filter(
            models.Q(issue_id__icontains=search) |
            models.Q(member__name__icontains=search) |
            models.Q(member__member_id__icontains=search) |
            models.Q(remarks__icontains=search)
        )

    if sort_by == "member_desc":
        issues = issues.order_by("-member__name")
    elif sort_by == "date_asc":
        issues = issues.order_by("issue_date")
    elif sort_by == "date_desc":
        issues = issues.order_by("-issue_date")
    else:
        issues = issues.order_by("-issue_date", "issue_id")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    members = LibraryMember.objects.all().order_by("name")
    books = Book.objects.all().order_by("name")

    default_due_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")

    return render(request, "portaluser/management/library-issue-book.html", {
        "issues": issues,
        "members": members,
        "books": books,
        "filter_member": filter_member,
        "filter_status": filter_status,
        "search": search,
        "sort_by": sort_by,
        "next_issue_id": _get_next_issue_id(),
        "today_date": date.today().strftime("%Y-%m-%d"),
        "default_due_date": default_due_date,
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def library_issue_book_export_pdf(request):
    issues = BookIssue.objects.select_related("member", "book").all().order_by("-issue_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/library-issue-book-print.html", {
        "issues": issues,
        "school_name": school.name if school else "Global International",
        "title": "Book Issues Report",
    })


def library_issue_book_export_excel(request):
    issues = BookIssue.objects.select_related("member", "book").all().order_by("-issue_date")

    filename = f"book_issues_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Date of Issue", "Due Date", "Issue To", "Books Issued", "Book Returned", "Issue Remarks", "Status"])

    for i in issues:
        writer.writerow([
            i.issue_id,
            i.issue_date.strftime("%d %b %Y") if i.issue_date else "-",
            i.due_date.strftime("%d %b %Y") if i.due_date else "-",
            i.member.name if i.member else "-",
            i.books_issued_count,
            i.books_returned_count,
            i.remarks or "-",
            i.status,
        ])

    return response


# ==========================================
# RETURN BOOK VIEWS
# ==========================================

def _get_next_return_id():
    for _ in range(100):
        candidate = f"RB853{random.randint(600, 999)}"
        if not BookReturn.objects.filter(return_id=candidate).exists():
            return candidate
    return f"RB{random.randint(100000, 999999)}"


def library_return_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_return" in request.POST:
            return_id = request.POST.get("return_id", "").strip()
            issue_pk = request.POST.get("issue_id", "").strip()
            member_pk = request.POST.get("member_id", "").strip()
            raw_issue_date = request.POST.get("issue_date", "")
            raw_due_date = request.POST.get("due_date", "")
            raw_return_date = request.POST.get("return_date", "")
            books_issued_count = request.POST.get("books_issued_count", "1").strip()
            books_returned_count = request.POST.get("books_returned_count", "1").strip()
            remarks = request.POST.get("remarks", "Book Returned").strip()

            if not return_id or BookReturn.objects.filter(return_id=return_id).exists():
                return_id = _get_next_return_id()

            issue_obj = BookIssue.objects.filter(pk=issue_pk).first() if issue_pk else None
            member = get_object_or_404(LibraryMember, pk=member_pk) if member_pk else (issue_obj.member if issue_obj else None)

            if not member:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Member is required."})
                messages.error(request, "Member is required.")
                return redirect("management:library-return")

            issue_date = _parse_date(raw_issue_date) if raw_issue_date else (issue_obj.issue_date if issue_obj else date.today())
            due_date = _parse_date(raw_due_date) if raw_due_date else (issue_obj.due_date if issue_obj else date.today())
            return_date = _parse_date(raw_return_date)

            try:
                issued_count = max(1, int(books_issued_count))
            except ValueError:
                issued_count = 1

            try:
                returned_count = max(1, int(books_returned_count))
            except ValueError:
                returned_count = 1

            status = "Returned"
            if returned_count < issued_count:
                status = "Partial Return"
            elif return_date > due_date:
                status = "Overdue Return"

            book_return = BookReturn.objects.create(
                return_id=return_id,
                issue=issue_obj,
                member=member,
                book=issue_obj.book if issue_obj else None,
                issue_date=issue_date,
                due_date=due_date,
                return_date=return_date,
                books_issued_count=issued_count,
                books_returned_count=returned_count,
                remarks=remarks or "Book Returned",
                status=status,
            )

            if issue_obj:
                issue_obj.books_returned_count += returned_count
                if issue_obj.books_returned_count >= issue_obj.books_issued_count:
                    issue_obj.status = "Returned"
                issue_obj.save()
                if issue_obj.book:
                    issue_obj.book.available += returned_count
                    issue_obj.book.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Book return recorded successfully."})
            messages.success(request, f"Book return recorded for '{member.name}' (Return ID: {return_id}) successfully.")
            return redirect("management:library-return")

        if "edit_return" in request.POST:
            return_obj = get_object_or_404(BookReturn, pk=request.POST.get("return_db_id"))
            raw_return_date = request.POST.get("return_date", "")
            books_returned_count = request.POST.get("books_returned_count", "1").strip()
            remarks = request.POST.get("remarks", "").strip()
            status = request.POST.get("status", "Returned").strip()

            if raw_return_date:
                return_obj.return_date = _parse_date(raw_return_date)

            try:
                return_obj.books_returned_count = max(1, int(books_returned_count))
            except ValueError:
                pass

            if remarks:
                return_obj.remarks = remarks
            if status:
                return_obj.status = status

            return_obj.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Return record updated successfully."})
            messages.success(request, f"Return record '{return_obj.return_id}' updated successfully.")
            return redirect("management:library-return")

        if "delete_return" in request.POST:
            return_obj = get_object_or_404(BookReturn, pk=request.POST.get("return_db_id"))
            return_code = return_obj.return_id
            return_obj.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Return record deleted successfully."})
            messages.success(request, f"Return record '{return_code}' deleted successfully.")
            return redirect("management:library-return")

    returns = BookReturn.objects.select_related("member", "book", "issue").all()

    filter_member = request.GET.get("filter_member", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_member:
        returns = returns.filter(member__name__icontains=filter_member)
    if filter_status:
        returns = returns.filter(status=filter_status)
    if search:
        returns = returns.filter(
            models.Q(return_id__icontains=search) |
            models.Q(member__name__icontains=search) |
            models.Q(remarks__icontains=search)
        )

    if sort_by == "member_desc":
        returns = returns.order_by("-member__name")
    elif sort_by == "date_asc":
        returns = returns.order_by("return_date")
    elif sort_by == "date_desc":
        returns = returns.order_by("-return_date")
    else:
        returns = returns.order_by("-return_date", "return_id")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    members = LibraryMember.objects.all().order_by("name")
    issues = BookIssue.objects.select_related("member").all().order_by("-issue_date")

    return render(request, "portaluser/management/library-return.html", {
        "returns": returns,
        "members": members,
        "issues": issues,
        "filter_member": filter_member,
        "filter_status": filter_status,
        "search": search,
        "sort_by": sort_by,
        "next_return_id": _get_next_return_id(),
        "today_date": date.today().strftime("%Y-%m-%d"),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def library_return_export_pdf(request):
    returns = BookReturn.objects.select_related("member", "book").all().order_by("-return_date")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/library-return-print.html", {
        "returns": returns,
        "school_name": school.name if school else "Global International",
        "title": "Book Returns Report",
    })


def library_return_export_excel(request):
    returns = BookReturn.objects.select_related("member", "book").all().order_by("-return_date")

    filename = f"book_returns_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Date of Issue", "Due Date", "Issue To", "Books Issued", "Book Returned", "Issue Remarks", "Status"])

    for r in returns:
        writer.writerow([
            r.return_id,
            r.issue_date.strftime("%d %b %Y") if r.issue_date else "-",
            r.due_date.strftime("%d %b %Y") if r.due_date else "-",
            r.member.name if r.member else "-",
            r.books_issued_count,
            r.books_returned_count,
            r.remarks or "-",
            r.status,
        ])

    return response


# ==========================================
# SPORTS VIEWS
# ==========================================

def _get_next_sport_id():
    for _ in range(100):
        candidate = f"SP826{random.randint(300, 999)}"
        if not Sport.objects.filter(sport_id=candidate).exists():
            return candidate
    return f"SP{random.randint(100000, 999999)}"


def sports_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_sport" in request.POST:
            sport_id = request.POST.get("sport_id", "").strip()
            name = request.POST.get("name", "").strip()
            coach = request.POST.get("coach", "").strip()
            started_year = request.POST.get("started_year", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Sport Name is required."})
                messages.error(request, "Sport Name is required.")
                return redirect("management:sports")

            if not sport_id or Sport.objects.filter(sport_id=sport_id).exists():
                sport_id = _get_next_sport_id()

            if not started_year:
                started_year = str(date.today().year)

            sport = Sport.objects.create(
                sport_id=sport_id,
                name=name,
                coach=coach,
                started_year=started_year,
            )
            if request.FILES.get("coach_avatar"):
                sport.coach_avatar = request.FILES["coach_avatar"]
                sport.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Sport added successfully."})
            messages.success(request, f"Sport '{name}' (ID: {sport_id}) added successfully.")
            return redirect("management:sports")

        if "edit_sport" in request.POST:
            sport = get_object_or_404(Sport, pk=request.POST.get("sport_db_id"))
            name = request.POST.get("name", "").strip()
            coach = request.POST.get("coach", "").strip()
            started_year = request.POST.get("started_year", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Sport Name is required."})
                messages.error(request, "Sport Name is required.")
                return redirect("management:sports")

            sport.name = name
            sport.coach = coach
            if started_year:
                sport.started_year = started_year
            if request.FILES.get("coach_avatar"):
                sport.coach_avatar = request.FILES["coach_avatar"]
            sport.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Sport updated successfully."})
            messages.success(request, f"Sport '{name}' updated successfully.")
            return redirect("management:sports")

        if "delete_sport" in request.POST:
            sport = get_object_or_404(Sport, pk=request.POST.get("sport_db_id"))
            sport_name = sport.name
            sport.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Sport deleted successfully."})
            messages.success(request, f"Sport '{sport_name}' deleted successfully.")
            return redirect("management:sports")

    sports = Sport.objects.all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_coach = request.GET.get("filter_coach", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_name:
        sports = sports.filter(name__icontains=filter_name)
    if filter_coach:
        sports = sports.filter(coach__icontains=filter_coach)
    if search:
        sports = sports.filter(
            models.Q(sport_id__icontains=search) |
            models.Q(name__icontains=search) |
            models.Q(coach__icontains=search) |
            models.Q(started_year__icontains=search)
        )

    if sort_by == "name_desc":
        sports = sports.order_by("-name")
    elif sort_by == "year_asc":
        sports = sports.order_by("started_year")
    elif sort_by == "year_desc":
        sports = sports.order_by("-started_year")
    else:
        sports = sports.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_sports = Sport.objects.all()

    return render(request, "portaluser/management/sports.html", {
        "sports": sports,
        "all_sports": all_sports,
        "filter_name": filter_name,
        "filter_coach": filter_coach,
        "search": search,
        "sort_by": sort_by,
        "next_sport_id": _get_next_sport_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def sports_export_pdf(request):
    sports = Sport.objects.all().order_by("name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/sports-print.html", {
        "sports": sports,
        "school_name": school.name if school else "Global International",
        "title": "Sports Report",
    })


def sports_export_excel(request):
    sports = Sport.objects.all().order_by("name")

    filename = f"sports_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Coach", "Started Year"])

    for s in sports:
        writer.writerow([
            s.sport_id,
            s.name,
            s.coach or "-",
            s.started_year or "-",
        ])

    return response


# ==========================================
# PLAYERS VIEWS
# ==========================================

def _get_next_player_id():
    for _ in range(100):
        candidate = f"SP8263{random.randint(20, 99)}"
        if not Player.objects.filter(player_id=candidate).exists():
            return candidate
    return f"SP{random.randint(100000, 999999)}"


def players_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_player" in request.POST:
            player_id = request.POST.get("player_id", "").strip()
            name = request.POST.get("name", "").strip()
            sport_id = request.POST.get("sport", "").strip()
            raw_date = request.POST.get("date_of_join", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Player Name is required."})
                messages.error(request, "Player Name is required.")
                return redirect("management:players")

            if not player_id or Player.objects.filter(player_id=player_id).exists():
                player_id = _get_next_player_id()

            sport_obj = Sport.objects.filter(pk=sport_id).first() if sport_id else None
            date_of_join = _parse_date(raw_date) if raw_date else date.today()

            player = Player.objects.create(
                player_id=player_id,
                name=name,
                sport=sport_obj,
                date_of_join=date_of_join,
            )
            if request.FILES.get("avatar"):
                player.avatar = request.FILES["avatar"]
                player.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Player added successfully."})
            messages.success(request, f"Player '{name}' (ID: {player_id}) added successfully.")
            return redirect("management:players")

        if "edit_player" in request.POST:
            player = get_object_or_404(Player, pk=request.POST.get("player_db_id"))
            name = request.POST.get("name", "").strip()
            sport_id = request.POST.get("sport", "").strip()
            raw_date = request.POST.get("date_of_join", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Player Name is required."})
                messages.error(request, "Player Name is required.")
                return redirect("management:players")

            player.name = name
            if sport_id:
                player.sport = Sport.objects.filter(pk=sport_id).first()
            if raw_date:
                player.date_of_join = _parse_date(raw_date)
            if request.FILES.get("avatar"):
                player.avatar = request.FILES["avatar"]
            player.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Player updated successfully."})
            messages.success(request, f"Player '{name}' updated successfully.")
            return redirect("management:players")

        if "delete_player" in request.POST:
            player = get_object_or_404(Player, pk=request.POST.get("player_db_id"))
            player_name = player.name
            player.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Player deleted successfully."})
            messages.success(request, f"Player '{player_name}' deleted successfully.")
            return redirect("management:players")

    players = Player.objects.select_related("sport").all()

    filter_player = request.GET.get("filter_player", "").strip()
    filter_sport = request.GET.get("filter_sport", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_player:
        players = players.filter(name__icontains=filter_player)
    if filter_sport:
        players = players.filter(sport__name__icontains=filter_sport)
    if search:
        players = players.filter(
            models.Q(player_id__icontains=search) |
            models.Q(name__icontains=search) |
            models.Q(sport__name__icontains=search)
        )

    if sort_by == "name_desc":
        players = players.order_by("-name")
    elif sort_by == "date_asc":
        players = players.order_by("date_of_join")
    elif sort_by == "date_desc":
        players = players.order_by("-date_of_join")
    else:
        players = players.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_sports = Sport.objects.all()

    return render(request, "portaluser/management/players.html", {
        "players": players,
        "all_sports": all_sports,
        "filter_player": filter_player,
        "filter_sport": filter_sport,
        "search": search,
        "sort_by": sort_by,
        "next_player_id": _get_next_player_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def players_export_pdf(request):
    players = Player.objects.select_related("sport").all().order_by("name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/players-print.html", {
        "players": players,
        "school_name": school.name if school else "Global International",
        "title": "Players Report",
    })


def players_export_excel(request):
    players = Player.objects.select_related("sport").all().order_by("name")

    filename = f"players_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Player Name", "Sports", "Date of Join"])

    for p in players:
        writer.writerow([
            p.player_id,
            p.name,
            p.sport.name if p.sport else "-",
            p.date_of_join.strftime("%d %b %Y") if p.date_of_join else "-",
        ])

    return response


# ==========================================
# HOSTEL VIEWS
# ==========================================

def _get_next_hostel_id():
    for _ in range(100):
        candidate = f"H823{random.randint(820, 899)}"
        if not Hostel.objects.filter(hostel_id=candidate).exists():
            return candidate
    return f"H{random.randint(100000, 999999)}"


def hostel_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_hostel" in request.POST:
            hostel_id = request.POST.get("hostel_id", "").strip()
            name = request.POST.get("name", "").strip()
            hostel_type = request.POST.get("hostel_type", "Boys").strip()
            address = request.POST.get("address", "").strip()
            intake_raw = request.POST.get("intake", "100").strip()
            description = request.POST.get("description", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Hostel Name is required."})
                messages.error(request, "Hostel Name is required.")
                return redirect("management:hostel-list")

            if not hostel_id or Hostel.objects.filter(hostel_id=hostel_id).exists():
                hostel_id = _get_next_hostel_id()

            try:
                intake = max(1, int(intake_raw))
            except ValueError:
                intake = 100

            Hostel.objects.create(
                hostel_id=hostel_id,
                name=name,
                hostel_type=hostel_type,
                address=address,
                intake=intake,
                description=description,
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel added successfully."})
            messages.success(request, f"Hostel '{name}' (ID: {hostel_id}) added successfully.")
            return redirect("management:hostel-list")

        if "edit_hostel" in request.POST:
            hostel = get_object_or_404(Hostel, pk=request.POST.get("hostel_db_id"))
            name = request.POST.get("name", "").strip()
            hostel_type = request.POST.get("hostel_type", "Boys").strip()
            address = request.POST.get("address", "").strip()
            intake_raw = request.POST.get("intake", "100").strip()
            description = request.POST.get("description", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Hostel Name is required."})
                messages.error(request, "Hostel Name is required.")
                return redirect("management:hostel-list")

            try:
                intake = max(1, int(intake_raw))
            except ValueError:
                intake = hostel.intake

            hostel.name = name
            hostel.hostel_type = hostel_type
            hostel.address = address
            hostel.intake = intake
            hostel.description = description
            hostel.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel updated successfully."})
            messages.success(request, f"Hostel '{name}' updated successfully.")
            return redirect("management:hostel-list")

        if "delete_hostel" in request.POST:
            hostel = get_object_or_404(Hostel, pk=request.POST.get("hostel_db_id"))
            hostel_name = hostel.name
            hostel.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel deleted successfully."})
            messages.success(request, f"Hostel '{hostel_name}' deleted successfully.")
            return redirect("management:hostel-list")

    hostels = Hostel.objects.all()

    filter_name = request.GET.get("filter_name", "").strip()
    filter_type = request.GET.get("filter_type", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_name:
        hostels = hostels.filter(name__icontains=filter_name)
    if filter_type:
        hostels = hostels.filter(hostel_type__iexact=filter_type)
    if search:
        hostels = hostels.filter(
            models.Q(hostel_id__icontains=search) |
            models.Q(name__icontains=search) |
            models.Q(address__icontains=search) |
            models.Q(description__icontains=search)
        )

    if sort_by == "name_desc":
        hostels = hostels.order_by("-name")
    elif sort_by == "intake_asc":
        hostels = hostels.order_by("intake")
    elif sort_by == "intake_desc":
        hostels = hostels.order_by("-intake")
    else:
        hostels = hostels.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()

    return render(request, "portaluser/management/hostel-list.html", {
        "hostels": hostels,
        "filter_name": filter_name,
        "filter_type": filter_type,
        "search": search,
        "sort_by": sort_by,
        "next_hostel_id": _get_next_hostel_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def hostel_export_pdf(request):
    hostels = Hostel.objects.all().order_by("name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/hostel-print.html", {
        "hostels": hostels,
        "school_name": school.name if school else "Global International",
        "title": "Hostel Report",
    })


def hostel_export_excel(request):
    hostels = Hostel.objects.all().order_by("name")

    filename = f"hostel_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Hostel Name", "Hostel Type", "Address", "Intake", "Description"])

    for h in hostels:
        writer.writerow([
            h.hostel_id,
            h.name,
            h.hostel_type,
            h.address or "-",
            h.intake,
            h.description or "-",
        ])

    return response


# ==========================================
# HOSTEL ROOMS VIEWS
# ==========================================

def _get_next_hostel_room_id():
    for _ in range(100):
        candidate = f"HR8193{random.randint(70, 99)}"
        if not HostelRoom.objects.filter(room_id=candidate).exists():
            return candidate
    return f"HR{random.randint(100000, 999999)}"


def hostel_rooms_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_hostel_room" in request.POST:
            room_id = request.POST.get("room_id", "").strip()
            room_no = request.POST.get("room_no", "").strip()
            hostel_id = request.POST.get("hostel", "").strip()
            room_type = request.POST.get("room_type", "One Bed").strip()
            no_of_beds_raw = request.POST.get("no_of_beds", "1").strip()
            cost_per_bed_raw = request.POST.get("cost_per_bed", "200.00").strip()

            if not room_no or not hostel_id:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Room No and Hostel Name are required."})
                messages.error(request, "Room No and Hostel Name are required.")
                return redirect("management:hostel-rooms")

            if not room_id or HostelRoom.objects.filter(room_id=room_id).exists():
                room_id = _get_next_hostel_room_id()

            hostel_obj = get_object_or_404(Hostel, pk=hostel_id)

            try:
                no_of_beds = max(1, int(no_of_beds_raw))
            except ValueError:
                no_of_beds = 1

            try:
                cost_per_bed = float(cost_per_bed_raw)
            except ValueError:
                cost_per_bed = 200.00

            HostelRoom.objects.create(
                room_id=room_id,
                room_no=room_no,
                hostel=hostel_obj,
                room_type=room_type,
                no_of_beds=no_of_beds,
                cost_per_bed=cost_per_bed,
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel Room added successfully."})
            messages.success(request, f"Hostel Room '{room_no}' (ID: {room_id}) added successfully.")
            return redirect("management:hostel-rooms")

        if "edit_hostel_room" in request.POST:
            room = get_object_or_404(HostelRoom, pk=request.POST.get("room_db_id"))
            room_no = request.POST.get("room_no", "").strip()
            hostel_id = request.POST.get("hostel", "").strip()
            room_type = request.POST.get("room_type", "One Bed").strip()
            no_of_beds_raw = request.POST.get("no_of_beds", "1").strip()
            cost_per_bed_raw = request.POST.get("cost_per_bed", "200.00").strip()

            if not room_no or not hostel_id:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Room No and Hostel Name are required."})
                messages.error(request, "Room No and Hostel Name are required.")
                return redirect("management:hostel-rooms")

            hostel_obj = get_object_or_404(Hostel, pk=hostel_id)

            try:
                no_of_beds = max(1, int(no_of_beds_raw))
            except ValueError:
                no_of_beds = room.no_of_beds

            try:
                cost_per_bed = float(cost_per_bed_raw)
            except ValueError:
                cost_per_bed = room.cost_per_bed

            room.room_no = room_no
            room.hostel = hostel_obj
            room.room_type = room_type
            room.no_of_beds = no_of_beds
            room.cost_per_bed = cost_per_bed
            room.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel Room updated successfully."})
            messages.success(request, f"Hostel Room '{room_no}' updated successfully.")
            return redirect("management:hostel-rooms")

        if "delete_hostel_room" in request.POST:
            room = get_object_or_404(HostelRoom, pk=request.POST.get("room_db_id"))
            room_no = room.room_no
            room.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel Room deleted successfully."})
            messages.success(request, f"Hostel Room '{room_no}' deleted successfully.")
            return redirect("management:hostel-rooms")

    rooms = HostelRoom.objects.select_related("hostel").all()

    filter_room_no = request.GET.get("filter_room_no", "").strip()
    filter_hostel = request.GET.get("filter_hostel", "").strip()
    filter_room_type = request.GET.get("filter_room_type", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_room_no:
        rooms = rooms.filter(room_no__icontains=filter_room_no)
    if filter_hostel:
        rooms = rooms.filter(hostel__name__icontains=filter_hostel)
    if filter_room_type:
        rooms = rooms.filter(room_type__icontains=filter_room_type)
    if search:
        rooms = rooms.filter(
            models.Q(room_id__icontains=search) |
            models.Q(room_no__icontains=search) |
            models.Q(hostel__name__icontains=search) |
            models.Q(room_type__icontains=search)
        )

    if sort_by == "room_desc":
        rooms = rooms.order_by("-room_no")
    elif sort_by == "cost_asc":
        rooms = rooms.order_by("cost_per_bed")
    elif sort_by == "cost_desc":
        rooms = rooms.order_by("-cost_per_bed")
    else:
        rooms = rooms.order_by("room_no")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_hostels = Hostel.objects.all()

    return render(request, "portaluser/management/hostel-rooms.html", {
        "rooms": rooms,
        "all_hostels": all_hostels,
        "filter_room_no": filter_room_no,
        "filter_hostel": filter_hostel,
        "filter_room_type": filter_room_type,
        "search": search,
        "sort_by": sort_by,
        "next_room_id": _get_next_hostel_room_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def hostel_rooms_export_pdf(request):
    rooms = HostelRoom.objects.select_related("hostel").all().order_by("room_no")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/hostel-rooms-print.html", {
        "rooms": rooms,
        "school_name": school.name if school else "Global International",
        "title": "Hostel Rooms Report",
    })


def hostel_rooms_export_excel(request):
    rooms = HostelRoom.objects.select_related("hostel").all().order_by("room_no")

    filename = f"hostel_rooms_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Room No", "Hostel Name", "Room Type", "No of Bed", "Cost per Bed"])

    for r in rooms:
        writer.writerow([
            r.room_id,
            r.room_no,
            r.hostel.name if r.hostel else "-",
            r.room_type,
            r.no_of_beds,
            f"{r.cost_per_bed:.2f}",
        ])

    return response


# ==========================================
# HOSTEL ROOM TYPE VIEWS
# ==========================================

def _get_next_room_type_id():
    for _ in range(100):
        candidate = f"RT8462{random.randint(10, 99)}"
        if not HostelRoomType.objects.filter(type_id=candidate).exists():
            return candidate
    return f"RT{random.randint(100000, 999999)}"


def hostel_room_type_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_room_type" in request.POST:
            type_id = request.POST.get("type_id", "").strip()
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Room Type Name is required."})
                messages.error(request, "Room Type Name is required.")
                return redirect("management:hostel-room-type")

            if not type_id or HostelRoomType.objects.filter(type_id=type_id).exists():
                type_id = _get_next_room_type_id()

            HostelRoomType.objects.create(
                type_id=type_id,
                name=name,
                description=description,
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel Room Type added successfully."})
            messages.success(request, f"Hostel Room Type '{name}' (ID: {type_id}) added successfully.")
            return redirect("management:hostel-room-type")

        if "edit_room_type" in request.POST:
            room_type = get_object_or_404(HostelRoomType, pk=request.POST.get("room_type_db_id"))
            type_id_val = request.POST.get("type_id", "").strip()
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Room Type Name is required."})
                messages.error(request, "Room Type Name is required.")
                return redirect("management:hostel-room-type")

            if type_id_val:
                room_type.type_id = type_id_val
            room_type.name = name
            room_type.description = description
            room_type.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel Room Type updated successfully."})
            messages.success(request, f"Hostel Room Type '{name}' updated successfully.")
            return redirect("management:hostel-room-type")

        if "delete_room_type" in request.POST:
            room_type = get_object_or_404(HostelRoomType, pk=request.POST.get("room_type_db_id"))
            room_type_name = room_type.name
            room_type.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Hostel Room Type deleted successfully."})
            messages.success(request, f"Hostel Room Type '{room_type_name}' deleted successfully.")
            return redirect("management:hostel-room-type")

    room_types = HostelRoomType.objects.all()

    filter_type = request.GET.get("filter_type", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_type:
        room_types = room_types.filter(name__iexact=filter_type)
    if search:
        room_types = room_types.filter(
            models.Q(type_id__icontains=search) |
            models.Q(name__icontains=search) |
            models.Q(description__icontains=search)
        )

    if sort_by == "name_desc":
        room_types = room_types.order_by("-name")
    elif sort_by == "date_asc":
        room_types = room_types.order_by("created_at")
    elif sort_by == "date_desc":
        room_types = room_types.order_by("-created_at")
    elif sort_by == "viewed":
        room_types = room_types.order_by("-updated_at")
    else:
        room_types = room_types.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_room_types = HostelRoomType.objects.all()
    type_names = HostelRoomType.objects.values_list("name", flat=True).distinct()

    return render(request, "portaluser/management/hostel-room-type.html", {
        "room_types": room_types,
        "all_room_types": all_room_types,
        "type_names": [n for n in type_names if n],
        "filter_type": filter_type,
        "search": search,
        "sort_by": sort_by,
        "next_type_id": _get_next_room_type_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def hostel_room_type_export_pdf(request):
    room_types = HostelRoomType.objects.all().order_by("name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/hostel-room-type-print.html", {
        "room_types": room_types,
        "school_name": school.name if school else "Global International",
        "title": "Hostel Room Type Report",
    })


def hostel_room_type_export_excel(request):
    room_types = HostelRoomType.objects.all().order_by("name")

    filename = f"hostel_room_types_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Room Type", "Description"])

    for rt in room_types:
        writer.writerow([
            rt.type_id,
            rt.name,
            rt.description or "-",
        ])

    return response


# ==========================================
# TRANSPORT ROUTES VIEWS
# ==========================================

def _get_next_route_id():
    numbers = []
    for rid in TransportRoute.objects.values_list("route_id", flat=True):
        if rid.startswith("R124") and len(rid) > 4 and rid[4:].isdigit():
            numbers.append(int(rid[4:]))
    candidate = max(numbers) + 1 if numbers else 500
    while TransportRoute.objects.filter(route_id=f"R124{candidate}").exists():
        candidate += 1
    return f"R124{candidate}"


def transport_routes_next_id(request):
    return JsonResponse({"success": True, "route_id": _get_next_route_id()})


def transport_routes_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_route" in request.POST:
            route_id = request.POST.get("route_id", "").strip()
            route_name = request.POST.get("route_name", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not route_name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Route Name is required."})
                messages.error(request, "Route Name is required.")
                return redirect("management:transport-routes")

            if not route_id or TransportRoute.objects.filter(route_id=route_id).exists():
                route_id = _get_next_route_id()

            route = TransportRoute.objects.create(
                route_id=route_id,
                route_name=route_name,
                status=status if status in ("Active", "Inactive") else "Active",
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Transport route added successfully."})
            messages.success(request, f"Route '{route_name}' (ID: {route_id}) added successfully.")
            return redirect("management:transport-routes")

        if "edit_route" in request.POST:
            route = get_object_or_404(TransportRoute, pk=request.POST.get("route_db_id"))
            route_id_val = request.POST.get("route_id", "").strip()
            route_name = request.POST.get("route_name", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not route_name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Route Name is required."})
                messages.error(request, "Route Name is required.")
                return redirect("management:transport-routes")

            if route_id_val:
                if TransportRoute.objects.filter(route_id=route_id_val).exclude(pk=route.pk).exists():
                    if is_ajax:
                        return JsonResponse({"success": False, "error": f"Route ID '{route_id_val}' already exists."})
                    messages.error(request, f"Route ID '{route_id_val}' already exists.")
                    return redirect("management:transport-routes")
                route.route_id = route_id_val
            route.route_name = route_name
            if status in ("Active", "Inactive"):
                route.status = status
            route.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Transport route updated successfully."})
            messages.success(request, f"Route '{route_name}' updated successfully.")
            return redirect("management:transport-routes")

        if "delete_route" in request.POST:
            route = get_object_or_404(TransportRoute, pk=request.POST.get("route_db_id"))
            route_name = route.route_name
            route.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Transport route deleted successfully."})
            messages.success(request, f"Route '{route_name}' deleted successfully.")
            return redirect("management:transport-routes")

    routes = TransportRoute.objects.all()

    filter_route = request.GET.get("filter_route", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_route:
        routes = routes.filter(route_name__icontains=filter_route)
    if filter_status in ("Active", "Inactive"):
        routes = routes.filter(status=filter_status)

    if sort_by == "name_desc":
        routes = routes.order_by("-route_name")
    elif sort_by == "date_asc":
        routes = routes.order_by("created_at")
    elif sort_by == "date_desc":
        routes = routes.order_by("-created_at")
    elif sort_by == "viewed":
        routes = routes.order_by("-updated_at")
    else:
        routes = routes.order_by("route_name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_routes = TransportRoute.objects.all()
    route_names = TransportRoute.objects.values_list("route_name", flat=True).distinct()

    return render(request, "portaluser/management/transport-routes.html", {
        "routes": routes,
        "all_routes": all_routes,
        "route_names": [n for n in route_names if n],
        "filter_route": filter_route,
        "filter_status": filter_status,
        "sort_by": sort_by,
        "next_route_id": _get_next_route_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def transport_routes_export_pdf(request):
    routes = TransportRoute.objects.all().order_by("route_name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/transport-routes-print.html", {
        "routes": routes,
        "school_name": school.name if school else "Global International",
        "title": "Transport Routes Report",
    })


def transport_routes_export_excel(request):
    routes = TransportRoute.objects.all().order_by("route_name")

    filename = f"transport_routes_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Route Name", "Status", "Added On"])

    for r in routes:
        writer.writerow([
            r.route_id,
            r.route_name,
            r.status,
            r.created_at.strftime("%d %b %Y") if r.created_at else "-",
        ])

    return response


# ==========================================
# TRANSPORT PICKUP POINTS VIEWS
# ==========================================

def _get_next_pickup_point_id():
    numbers = []
    for pp in TransportPickupPoint.objects.values_list("pickup_point_id", flat=True):
        if pp.startswith("PP124") and len(pp) > 5 and pp[5:].isdigit():
            numbers.append(int(pp[5:]))
    candidate = max(numbers) + 1 if numbers else 500
    while TransportPickupPoint.objects.filter(pickup_point_id=f"PP124{candidate}").exists():
        candidate += 1
    return f"PP124{candidate}"


def transport_pickup_points_next_id(request):
    return JsonResponse({"success": True, "pickup_point_id": _get_next_pickup_point_id()})


def transport_pickup_points_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_pickup_point" in request.POST:
            pickup_point_id = request.POST.get("pickup_point_id", "").strip()
            pickup_point = request.POST.get("pickup_point", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not pickup_point:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Pickup Point is required."})
                messages.error(request, "Pickup Point is required.")
                return redirect("management:transport-pickup-points")

            if not pickup_point_id or TransportPickupPoint.objects.filter(pickup_point_id=pickup_point_id).exists():
                pickup_point_id = _get_next_pickup_point_id()

            TransportPickupPoint.objects.create(
                pickup_point_id=pickup_point_id,
                pickup_point=pickup_point,
                status=status if status in ("Active", "Inactive") else "Active",
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Pickup point added successfully."})
            messages.success(request, f"Pickup point '{pickup_point}' (ID: {pickup_point_id}) added successfully.")
            return redirect("management:transport-pickup-points")

        if "edit_pickup_point" in request.POST:
            pp = get_object_or_404(TransportPickupPoint, pk=request.POST.get("pickup_point_db_id"))
            pickup_point_id_val = request.POST.get("pickup_point_id", "").strip()
            pickup_point = request.POST.get("pickup_point", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not pickup_point:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Pickup Point is required."})
                messages.error(request, "Pickup Point is required.")
                return redirect("management:transport-pickup-points")

            if pickup_point_id_val:
                if TransportPickupPoint.objects.filter(pickup_point_id=pickup_point_id_val).exclude(pk=pp.pk).exists():
                    if is_ajax:
                        return JsonResponse({"success": False, "error": f"Pickup Point ID '{pickup_point_id_val}' already exists."})
                    messages.error(request, f"Pickup Point ID '{pickup_point_id_val}' already exists.")
                    return redirect("management:transport-pickup-points")
                pp.pickup_point_id = pickup_point_id_val
            pp.pickup_point = pickup_point
            if status in ("Active", "Inactive"):
                pp.status = status
            pp.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Pickup point updated successfully."})
            messages.success(request, f"Pickup point '{pickup_point}' updated successfully.")
            return redirect("management:transport-pickup-points")

        if "delete_pickup_point" in request.POST:
            pp = get_object_or_404(TransportPickupPoint, pk=request.POST.get("pickup_point_db_id"))
            pp_name = pp.pickup_point
            pp.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Pickup point deleted successfully."})
            messages.success(request, f"Pickup point '{pp_name}' deleted successfully.")
            return redirect("management:transport-pickup-points")

    pickup_points = TransportPickupPoint.objects.all()

    filter_point = request.GET.get("filter_point", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_point:
        pickup_points = pickup_points.filter(pickup_point__icontains=filter_point)
    if filter_status in ("Active", "Inactive"):
        pickup_points = pickup_points.filter(status=filter_status)

    if sort_by == "name_desc":
        pickup_points = pickup_points.order_by("-pickup_point")
    elif sort_by == "date_asc":
        pickup_points = pickup_points.order_by("created_at")
    elif sort_by == "date_desc":
        pickup_points = pickup_points.order_by("-created_at")
    elif sort_by == "viewed":
        pickup_points = pickup_points.order_by("-updated_at")
    else:
        pickup_points = pickup_points.order_by("pickup_point")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_pickup_points = TransportPickupPoint.objects.all()
    point_names = TransportPickupPoint.objects.values_list("pickup_point", flat=True).distinct()

    return render(request, "portaluser/management/transport-pickup-points.html", {
        "pickup_points": pickup_points,
        "all_pickup_points": all_pickup_points,
        "point_names": [n for n in point_names if n],
        "filter_point": filter_point,
        "filter_status": filter_status,
        "sort_by": sort_by,
        "next_pickup_point_id": _get_next_pickup_point_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def transport_pickup_points_export_pdf(request):
    pickup_points = TransportPickupPoint.objects.all().order_by("pickup_point")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/transport-pickup-points-print.html", {
        "pickup_points": pickup_points,
        "school_name": school.name if school else "Global International",
        "title": "Transport Pickup Points Report",
    })


def transport_pickup_points_export_excel(request):
    pickup_points = TransportPickupPoint.objects.all().order_by("pickup_point")

    filename = f"transport_pickup_points_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Pickup Point", "Status", "Added On"])

    for p in pickup_points:
        writer.writerow([
            p.pickup_point_id,
            p.pickup_point,
            p.status,
            p.created_at.strftime("%d %b %Y") if p.created_at else "-",
        ])

    return response


# ==========================================
# TRANSPORT VEHICLE DRIVERS VIEWS
# ==========================================

def _get_next_driver_id():
    numbers = []
    for did in TransportVehicleDriver.objects.values_list("driver_id", flat=True):
        if did.startswith("D") and len(did) > 1 and did[1:].isdigit():
            numbers.append(int(did[1:]))
    candidate = max(numbers) + 1 if numbers else 482
    while TransportVehicleDriver.objects.filter(driver_id=f"D{candidate:04d}").exists():
        candidate += 1
    return f"D{candidate:04d}"


def transport_vehicle_drivers_next_id(request):
    return JsonResponse({"success": True, "driver_id": _get_next_driver_id()})


def transport_vehicle_drivers_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_driver" in request.POST:
            name = request.POST.get("name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            driver_license_no = request.POST.get("driver_license_no", "").strip()
            address = request.POST.get("address", "").strip()
            status = request.POST.get("status", "Active").strip()

            driver_id_val = request.POST.get("driver_id", "").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Driver Name is required."})
                messages.error(request, "Driver Name is required.")
                return redirect("management:transport-vehicle-drivers")

            if driver_id_val:
                if TransportVehicleDriver.objects.filter(driver_id=driver_id_val).exists():
                    if is_ajax:
                        return JsonResponse({"success": False, "error": f"Driver ID '{driver_id_val}' already exists."})
                    messages.error(request, f"Driver ID '{driver_id_val}' already exists.")
                    return redirect("management:transport-vehicle-drivers")
                driver_id = driver_id_val
            else:
                driver_id = _get_next_driver_id()

            TransportVehicleDriver.objects.create(
                driver_id=driver_id,
                name=name,
                phone_number=phone_number,
                driver_license_no=driver_license_no,
                address=address,
                status=status if status in ("Active", "Inactive") else "Active",
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle driver added successfully."})
            messages.success(request, f"Driver '{name}' (ID: {driver_id}) added successfully.")
            return redirect("management:transport-vehicle-drivers")

        if "edit_driver" in request.POST:
            driver = get_object_or_404(TransportVehicleDriver, pk=request.POST.get("driver_db_id"))
            driver_id_val = request.POST.get("driver_id", "").strip()
            name = request.POST.get("name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            driver_license_no = request.POST.get("driver_license_no", "").strip()
            address = request.POST.get("address", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not name:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Driver Name is required."})
                messages.error(request, "Driver Name is required.")
                return redirect("management:transport-vehicle-drivers")

            if driver_id_val:
                if TransportVehicleDriver.objects.filter(driver_id=driver_id_val).exclude(pk=driver.pk).exists():
                    if is_ajax:
                        return JsonResponse({"success": False, "error": f"Driver ID '{driver_id_val}' already exists."})
                    messages.error(request, f"Driver ID '{driver_id_val}' already exists.")
                    return redirect("management:transport-vehicle-drivers")
                driver.driver_id = driver_id_val
            driver.name = name
            driver.phone_number = phone_number
            driver.driver_license_no = driver_license_no
            driver.address = address
            if status in ("Active", "Inactive"):
                driver.status = status
            driver.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle driver updated successfully."})
            messages.success(request, f"Driver '{name}' updated successfully.")
            return redirect("management:transport-vehicle-drivers")

        if "delete_driver" in request.POST:
            driver = get_object_or_404(TransportVehicleDriver, pk=request.POST.get("driver_db_id"))
            driver_name = driver.name
            driver.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle driver deleted successfully."})
            messages.success(request, f"Driver '{driver_name}' deleted successfully.")
            return redirect("management:transport-vehicle-drivers")

    drivers = TransportVehicleDriver.objects.all()

    filter_driver = request.GET.get("filter_driver", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_driver:
        drivers = drivers.filter(name__icontains=filter_driver)
    if filter_status in ("Active", "Inactive"):
        drivers = drivers.filter(status=filter_status)
    if search:
        drivers = drivers.filter(
            models.Q(driver_id__icontains=search) |
            models.Q(name__icontains=search) |
            models.Q(phone_number__icontains=search) |
            models.Q(driver_license_no__icontains=search) |
            models.Q(address__icontains=search)
        )

    if sort_by == "name_desc":
        drivers = drivers.order_by("-name")
    elif sort_by == "date_asc":
        drivers = drivers.order_by("created_at")
    elif sort_by == "date_desc":
        drivers = drivers.order_by("-created_at")
    elif sort_by == "viewed":
        drivers = drivers.order_by("-updated_at")
    else:
        drivers = drivers.order_by("name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_drivers = TransportVehicleDriver.objects.all()
    driver_names = TransportVehicleDriver.objects.values_list("name", flat=True).distinct()

    return render(request, "portaluser/management/transport-vehicle-drivers.html", {
        "drivers": drivers,
        "all_drivers": all_drivers,
        "driver_names": [n for n in driver_names if n],
        "filter_driver": filter_driver,
        "filter_status": filter_status,
        "search": search,
        "sort_by": sort_by,
        "next_driver_id": _get_next_driver_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def transport_vehicle_drivers_export_pdf(request):
    drivers = TransportVehicleDriver.objects.all().order_by("name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/transport-vehicle-drivers-print.html", {
        "drivers": drivers,
        "school_name": school.name if school else "Global International",
        "title": "Transport Vehicle Drivers Report",
    })


def transport_vehicle_drivers_export_excel(request):
    drivers = TransportVehicleDriver.objects.all().order_by("name")

    filename = f"transport_vehicle_drivers_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Driver", "Phone Number", "Driver License No", "Address", "Status"])

    for d in drivers:
        writer.writerow([
            d.driver_id,
            d.name,
            d.phone_number or "-",
            d.driver_license_no or "-",
            d.address or "-",
            d.status,
        ])

    return response


# ==========================================
# TRANSPORT VEHICLE VIEWS
# ==========================================

def _get_next_vehicle_id():
    numbers = []
    for vid in TransportVehicle.objects.values_list("vehicle_id", flat=True):
        if vid and vid.startswith("B8048") and vid[5:].isdigit():
            numbers.append(int(vid[5:]))
    candidate = max(numbers) + 1 if numbers else 1
    while TransportVehicle.objects.filter(vehicle_id=f"B8048{candidate}").exists():
        candidate += 1
    return f"B8048{candidate}"


def _parse_year(value):
    value = (value or "").strip()
    if not value:
        return ""
    try:
        return str(_parse_date(value).year)
    except Exception:
        return value


def transport_vehicles_next_id(request):
    return JsonResponse({"success": True, "vehicle_id": _get_next_vehicle_id()})


def transport_vehicles_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_vehicle" in request.POST:
            vehicle_id = request.POST.get("vehicle_id", "").strip()
            vehicle_no = request.POST.get("vehicle_no", "").strip()
            vehicle_model = request.POST.get("vehicle_model", "").strip()
            made_of_year = _parse_year(request.POST.get("made_of_year", ""))
            registration_no = request.POST.get("registration_no", "").strip()
            chassis_no = request.POST.get("chassis_no", "").strip()
            seat_capacity_raw = request.POST.get("seat_capacity", "1").strip()
            gps_device_id = request.POST.get("gps_device_id", "").strip()
            driver_pk = request.POST.get("driver", "").strip()
            driver_license_no = request.POST.get("driver_license_no", "").strip()
            driver_contact_no = request.POST.get("driver_contact_no", "").strip()
            driver_address = request.POST.get("driver_address", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not vehicle_no:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Vehicle No is required."})
                messages.error(request, "Vehicle No is required.")
                return redirect("management:transport-vehicle")

            if not vehicle_id or TransportVehicle.objects.filter(vehicle_id=vehicle_id).exists():
                vehicle_id = _get_next_vehicle_id()

            try:
                seat_capacity = max(1, int(seat_capacity_raw))
            except ValueError:
                seat_capacity = 1

            driver_obj = TransportVehicleDriver.objects.filter(pk=driver_pk).first() if driver_pk else None

            TransportVehicle.objects.create(
                vehicle_id=vehicle_id,
                vehicle_no=vehicle_no,
                vehicle_model=vehicle_model,
                made_of_year=made_of_year,
                registration_no=registration_no,
                chassis_no=chassis_no,
                seat_capacity=seat_capacity,
                gps_device_id=gps_device_id,
                driver=driver_obj,
                driver_license_no=driver_license_no,
                driver_contact_no=driver_contact_no,
                driver_address=driver_address,
                status=status if status in ("Active", "Inactive") else "Active",
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle added successfully."})
            messages.success(request, f"Vehicle '{vehicle_no}' (ID: {vehicle_id}) added successfully.")
            return redirect("management:transport-vehicle")

        if "edit_vehicle" in request.POST:
            vehicle = get_object_or_404(TransportVehicle, pk=request.POST.get("vehicle_db_id"))
            vehicle_id_val = request.POST.get("vehicle_id", "").strip()
            vehicle_no = request.POST.get("vehicle_no", "").strip()
            vehicle_model = request.POST.get("vehicle_model", "").strip()
            made_of_year = _parse_year(request.POST.get("made_of_year", ""))
            registration_no = request.POST.get("registration_no", "").strip()
            chassis_no = request.POST.get("chassis_no", "").strip()
            seat_capacity_raw = request.POST.get("seat_capacity", "1").strip()
            gps_device_id = request.POST.get("gps_device_id", "").strip()
            driver_pk = request.POST.get("driver", "").strip()
            driver_license_no = request.POST.get("driver_license_no", "").strip()
            driver_contact_no = request.POST.get("driver_contact_no", "").strip()
            driver_address = request.POST.get("driver_address", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not vehicle_no:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Vehicle No is required."})
                messages.error(request, "Vehicle No is required.")
                return redirect("management:transport-vehicle")

            if vehicle_id_val:
                if TransportVehicle.objects.filter(vehicle_id=vehicle_id_val).exclude(pk=vehicle.pk).exists():
                    if is_ajax:
                        return JsonResponse({"success": False, "error": f"Vehicle ID '{vehicle_id_val}' already exists."})
                    messages.error(request, f"Vehicle ID '{vehicle_id_val}' already exists.")
                    return redirect("management:transport-vehicle")
                vehicle.vehicle_id = vehicle_id_val

            try:
                seat_capacity = max(1, int(seat_capacity_raw))
            except ValueError:
                seat_capacity = vehicle.seat_capacity

            driver_obj = TransportVehicleDriver.objects.filter(pk=driver_pk).first() if driver_pk else None

            vehicle.vehicle_no = vehicle_no
            vehicle.vehicle_model = vehicle_model
            if made_of_year:
                vehicle.made_of_year = made_of_year
            vehicle.registration_no = registration_no
            vehicle.chassis_no = chassis_no
            vehicle.seat_capacity = seat_capacity
            vehicle.gps_device_id = gps_device_id
            vehicle.driver = driver_obj
            vehicle.driver_license_no = driver_license_no
            vehicle.driver_contact_no = driver_contact_no
            vehicle.driver_address = driver_address
            if status in ("Active", "Inactive"):
                vehicle.status = status
            vehicle.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle updated successfully."})
            messages.success(request, f"Vehicle '{vehicle_no}' updated successfully.")
            return redirect("management:transport-vehicle")

        if "delete_vehicle" in request.POST:
            vehicle = get_object_or_404(TransportVehicle, pk=request.POST.get("vehicle_db_id"))
            vehicle_no = vehicle.vehicle_no
            vehicle.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle deleted successfully."})
            messages.success(request, f"Vehicle '{vehicle_no}' deleted successfully.")
            return redirect("management:transport-vehicle")

    vehicles = TransportVehicle.objects.select_related("driver").all()

    filter_vehicle_no = request.GET.get("filter_vehicle_no", "").strip()
    filter_model = request.GET.get("filter_model", "").strip()
    filter_driver = request.GET.get("filter_driver", "").strip()
    filter_gps_device = request.GET.get("filter_gps_device", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_vehicle_no:
        vehicles = vehicles.filter(vehicle_no__icontains=filter_vehicle_no)
    if filter_model:
        vehicles = vehicles.filter(vehicle_model__iexact=filter_model)
    if filter_driver:
        vehicles = vehicles.filter(driver__name__icontains=filter_driver)
    if filter_gps_device:
        vehicles = vehicles.filter(gps_device_id__icontains=filter_gps_device)
    if filter_status in ("Active", "Inactive"):
        vehicles = vehicles.filter(status=filter_status)

    if sort_by == "name_desc":
        vehicles = vehicles.order_by("-vehicle_no")
    elif sort_by == "date_asc":
        vehicles = vehicles.order_by("created_at")
    elif sort_by == "date_desc":
        vehicles = vehicles.order_by("-created_at")
    elif sort_by == "viewed":
        vehicles = vehicles.order_by("-updated_at")
    else:
        vehicles = vehicles.order_by("vehicle_no")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_vehicles = TransportVehicle.objects.all()
    all_drivers = TransportVehicleDriver.objects.all().order_by("name")
    vehicle_numbers = TransportVehicle.objects.values_list("vehicle_no", flat=True).distinct()
    vehicle_models = TransportVehicle.objects.values_list("vehicle_model", flat=True).distinct()
    gps_devices = TransportVehicle.objects.values_list("gps_device_id", flat=True).distinct()

    return render(request, "portaluser/management/transport-vehicle.html", {
        "vehicles": vehicles,
        "all_vehicles": all_vehicles,
        "all_drivers": all_drivers,
        "vehicle_numbers": [v for v in vehicle_numbers if v],
        "vehicle_models": [m for m in vehicle_models if m],
        "gps_devices": [g for g in gps_devices if g],
        "filter_vehicle_no": filter_vehicle_no,
        "filter_model": filter_model,
        "filter_driver": filter_driver,
        "filter_gps_device": filter_gps_device,
        "filter_status": filter_status,
        "sort_by": sort_by,
        "next_vehicle_id": _get_next_vehicle_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def transport_vehicles_export_pdf(request):
    vehicles = TransportVehicle.objects.select_related("driver").all().order_by("vehicle_no")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/transport-vehicle-print.html", {
        "vehicles": vehicles,
        "school_name": school.name if school else "Global International",
        "title": "Transport Vehicle Report",
    })


def transport_vehicles_export_excel(request):
    vehicles = TransportVehicle.objects.select_related("driver").all().order_by("vehicle_no")

    filename = f"transport_vehicles_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Vehicle No", "Vehicle Model", "Made of Year", "Registration No", "Chassis No", "Seat Capacity", "GPS Device ID", "Driver", "Driver License", "Driver Contact No", "Driver Address", "Status"])

    for v in vehicles:
        writer.writerow([
            v.vehicle_id,
            v.vehicle_no,
            v.vehicle_model or "-",
            v.made_of_year or "-",
            v.registration_no or "-",
            v.chassis_no or "-",
            v.seat_capacity,
            v.gps_device_id or "-",
            v.driver.name if v.driver else "-",
            v.driver_license_no or "-",
            v.driver_contact_no or "-",
            v.driver_address or "-",
            v.status,
        ])

    return response


# ==========================================
# TRANSPORT ASSIGN VEHICLE VIEWS
# ==========================================

def _get_next_assign_vehicle_id():
    numbers = []
    for aid in TransportAssignVehicle.objects.values_list("assign_id", flat=True):
        if aid.startswith("AV124") and len(aid) > 5 and aid[5:].isdigit():
            numbers.append(int(aid[5:]))
    candidate = max(numbers) + 1 if numbers else 500
    while TransportAssignVehicle.objects.filter(assign_id=f"AV124{candidate}").exists():
        candidate += 1
    return f"AV124{candidate}"


def transport_assign_vehicles_next_id(request):
    return JsonResponse({"success": True, "assign_id": _get_next_assign_vehicle_id()})


def transport_assign_vehicles_list(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        if "add_assign_vehicle" in request.POST:
            assign_id = request.POST.get("assign_id", "").strip()
            route_pk = request.POST.get("route", "").strip()
            pickup_point_pk = request.POST.get("pickup_point", "").strip()
            vehicle_pk = request.POST.get("vehicle", "").strip()
            status = request.POST.get("status", "Active").strip()

            if not route_pk or not pickup_point_pk or not vehicle_pk:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Route, Pickup Point and Vehicle are required."})
                messages.error(request, "Route, Pickup Point and Vehicle are required.")
                return redirect("management:transport-assign-vehicle")

            if not assign_id or TransportAssignVehicle.objects.filter(assign_id=assign_id).exists():
                assign_id = _get_next_assign_vehicle_id()

            route = TransportRoute.objects.filter(pk=route_pk).first()
            pickup_point = TransportPickupPoint.objects.filter(pk=pickup_point_pk).first()
            vehicle = TransportVehicle.objects.filter(pk=vehicle_pk).first()

            TransportAssignVehicle.objects.create(
                assign_id=assign_id,
                route=route,
                pickup_point=pickup_point,
                vehicle=vehicle,
                status=status if status in ("Active", "Inactive") else "Active",
            )

            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle assigned successfully."})
            vehicle_label = vehicle.vehicle_no if vehicle else "-"
            messages.success(request, f"Vehicle '{vehicle_label}' assigned (ID: {assign_id}) successfully.")
            return redirect("management:transport-assign-vehicle")

        if "edit_assign_vehicle" in request.POST:
            assign = get_object_or_404(TransportAssignVehicle, pk=request.POST.get("assign_db_id"))
            assign_id_val = request.POST.get("assign_id", "").strip()
            route_pk = request.POST.get("route", "").strip()
            pickup_point_pk = request.POST.get("pickup_point", "").strip()
            vehicle_pk = request.POST.get("vehicle", "").strip()
            status = request.POST.get("status", "").strip()

            if not route_pk or not pickup_point_pk or not vehicle_pk:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Route, Pickup Point and Vehicle are required."})
                messages.error(request, "Route, Pickup Point and Vehicle are required.")
                return redirect("management:transport-assign-vehicle")

            if assign_id_val:
                if TransportAssignVehicle.objects.filter(assign_id=assign_id_val).exclude(pk=assign.pk).exists():
                    if is_ajax:
                        return JsonResponse({"success": False, "error": f"Assign ID '{assign_id_val}' already exists."})
                    messages.error(request, f"Assign ID '{assign_id_val}' already exists.")
                    return redirect("management:transport-assign-vehicle")
                assign.assign_id = assign_id_val

            assign.route = TransportRoute.objects.filter(pk=route_pk).first()
            assign.pickup_point = TransportPickupPoint.objects.filter(pk=pickup_point_pk).first()
            assign.vehicle = TransportVehicle.objects.filter(pk=vehicle_pk).first()
            if status in ("Active", "Inactive"):
                assign.status = status
            assign.save()

            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle assignment updated successfully."})
            messages.success(request, f"Vehicle assignment '{assign.assign_id}' updated successfully.")
            return redirect("management:transport-assign-vehicle")

        if "delete_assign_vehicle" in request.POST:
            assign = get_object_or_404(TransportAssignVehicle, pk=request.POST.get("assign_db_id"))
            assign_code = assign.assign_id
            assign.delete()
            if is_ajax:
                return JsonResponse({"success": True, "message": "Vehicle assignment deleted successfully."})
            messages.success(request, f"Vehicle assignment '{assign_code}' deleted successfully.")
            return redirect("management:transport-assign-vehicle")

    assignments = TransportAssignVehicle.objects.select_related("route", "pickup_point", "vehicle", "vehicle__driver").all()

    filter_route = request.GET.get("filter_route", "").strip()
    filter_point = request.GET.get("filter_point", "").strip()
    filter_vehicle_no = request.GET.get("filter_vehicle_no", "").strip()
    filter_driver = request.GET.get("filter_driver", "").strip()
    filter_status = request.GET.get("filter_status", "").strip()
    filter_field = request.GET.get("filter_field", "").strip()
    sort_by = request.GET.get("sort_by", "").strip()

    if filter_route:
        assignments = assignments.filter(route__route_name__icontains=filter_route)
    if filter_point:
        assignments = assignments.filter(pickup_point__pickup_point__icontains=filter_point)
    if filter_vehicle_no:
        assignments = assignments.filter(vehicle__vehicle_no__icontains=filter_vehicle_no)
    if filter_driver:
        assignments = assignments.filter(vehicle__driver__name__icontains=filter_driver)
    if filter_status in ("Active", "Inactive"):
        assignments = assignments.filter(status=filter_status)
    if filter_field:
        assignments = assignments.filter(
            models.Q(assign_id__icontains=filter_field) |
            models.Q(route__route_name__icontains=filter_field) |
            models.Q(pickup_point__pickup_point__icontains=filter_field) |
            models.Q(vehicle__vehicle_no__icontains=filter_field) |
            models.Q(vehicle__driver__name__icontains=filter_field) |
            models.Q(status__icontains=filter_field)
        )

    if sort_by == "route_desc":
        assignments = assignments.order_by("-route__route_name")
    elif sort_by == "date_asc":
        assignments = assignments.order_by("created_at")
    elif sort_by == "date_desc":
        assignments = assignments.order_by("-created_at")
    elif sort_by == "viewed":
        assignments = assignments.order_by("-updated_at")
    else:
        assignments = assignments.order_by("route__route_name")

    school = School.objects.filter(is_active=True).first()
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    all_routes = TransportRoute.objects.all().order_by("route_name")
    all_pickup_points = TransportPickupPoint.objects.all().order_by("pickup_point")
    all_vehicles = TransportVehicle.objects.select_related("driver").all().order_by("vehicle_no")
    all_drivers = TransportVehicleDriver.objects.all().order_by("name")
    route_names = TransportRoute.objects.values_list("route_name", flat=True).distinct()
    point_names = TransportPickupPoint.objects.values_list("pickup_point", flat=True).distinct()
    vehicle_numbers = TransportVehicle.objects.values_list("vehicle_no", flat=True).distinct()
    driver_names = TransportVehicleDriver.objects.values_list("name", flat=True).distinct()

    return render(request, "portaluser/management/transport-assign-vehicle.html", {
        "assignments": assignments,
        "all_routes": all_routes,
        "all_pickup_points": all_pickup_points,
        "all_vehicles": all_vehicles,
        "all_drivers": all_drivers,
        "route_names": [n for n in route_names if n],
        "point_names": [n for n in point_names if n],
        "vehicle_numbers": [v for v in vehicle_numbers if v],
        "driver_names": [n for n in driver_names if n],
        "filter_route": filter_route,
        "filter_point": filter_point,
        "filter_vehicle_no": filter_vehicle_no,
        "filter_driver": filter_driver,
        "filter_status": filter_status,
        "filter_field": filter_field,
        "sort_by": sort_by,
        "next_assign_id": _get_next_assign_vehicle_id(),
        "school_name": school.name if school else "Global International",
        "current_academic_year": current_academic_year,
        "academic_years": AcademicYear.objects.all().order_by("-start_date"),
    })


def transport_assign_vehicles_export_pdf(request):
    assignments = TransportAssignVehicle.objects.select_related("route", "pickup_point", "vehicle", "vehicle__driver").all().order_by("route__route_name")
    school = School.objects.filter(is_active=True).first()

    return render(request, "portaluser/management/transport-assign-vehicle-print.html", {
        "assignments": assignments,
        "school_name": school.name if school else "Global International",
        "title": "Transport Assign Vehicle Report",
    })


def transport_assign_vehicles_export_excel(request):
    assignments = TransportAssignVehicle.objects.select_related("route", "pickup_point", "vehicle", "vehicle__driver").all().order_by("route__route_name")

    filename = f"transport_assign_vehicles_{date.today().strftime('%Y%m%d')}"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(["ID", "Route", "Pickup Point", "Vehicle No", "Driver", "Driver Contact No", "Status"])

    for a in assignments:
        writer.writerow([
            a.assign_id,
            a.route.route_name if a.route else "-",
            a.pickup_point.pickup_point if a.pickup_point else "-",
            a.vehicle.vehicle_no if a.vehicle else "-",
            a.vehicle.driver.name if a.vehicle and a.vehicle.driver else "-",
            a.vehicle.driver_contact_no if a.vehicle else "-",
            a.status,
        ])

    return response
