"""Seed initial payroll records from existing teachers and staff."""
from django.db import migrations
from django.utils import timezone


def _parse_amount(value, default):
    if value is None:
        return default
    text = str(value).replace(",", "").replace("$", "").strip()
    if not text:
        return default
    try:
        return float(text)
    except (ValueError, TypeError):
        return default


def _build_breakdown(basic):
    hra = round(basic * 0.20, 2)
    da = round(basic * 0.10, 2)
    medical = 1000.0
    other_allowance = 500.0
    bonus = 0.0
    tax = round(basic * 0.05, 2)
    pf = round(basic * 0.12, 2)
    insurance = 200.0
    other_deduction = 0.0
    total_earnings = basic + hra + da + medical + other_allowance + bonus
    total_deductions = tax + pf + insurance + other_deduction
    net = round(total_earnings - total_deductions, 2)
    return {
        "basic_salary": basic,
        "house_rent_allowance": hra,
        "dearness_allowance": da,
        "medical_allowance": medical,
        "other_allowance": other_allowance,
        "bonus": bonus,
        "tax_deduction": tax,
        "provident_fund": pf,
        "insurance": insurance,
        "other_deduction": other_deduction,
        "net_salary": net,
    }


def seed_payroll(apps, schema_editor):
    Payroll = apps.get_model("hrm", "Payroll")
    Teacher = apps.get_model("people", "Teacher")
    Staff = apps.get_model("people", "Staff")

    if Payroll.objects.exists():
        return

    today = timezone.localdate()
    month = today.strftime("%B")
    year = str(today.year)

    payrolls = []
    counter = 0
    for teacher in Teacher.objects.filter(status="active").order_by("pk"):
        basic = _parse_amount(teacher.basic_salary, 15000)
        amounts = _build_breakdown(basic)
        counter += 1
        is_generated = counter % 4 == 0
        payrolls.append(Payroll(
            code=f"P{738197 - counter}",
            teacher=teacher,
            name=teacher.name,
            department="Teaching",
            designation="Teacher",
            phone=teacher.phone or teacher.primary_contact_number or "",
            month=month,
            year=year,
            status="generated" if is_generated else "paid",
            pay_date=None if is_generated else today,
            **amounts,
        ))

    for staff in Staff.objects.filter(status="active").order_by("pk"):
        basic = _parse_amount(staff.basic_salary, 12000)
        amounts = _build_breakdown(basic)
        counter += 1
        is_generated = counter % 4 == 0
        payrolls.append(Payroll(
            code=f"P{738197 - counter}",
            staff=staff,
            name=staff.name,
            department=staff.department or "Management",
            designation=staff.designation or "Staff",
            phone=staff.phone or staff.primary_contact_number or "",
            month=month,
            year=year,
            status="generated" if is_generated else "paid",
            pay_date=None if is_generated else today,
            **amounts,
        ))

    if payrolls:
        Payroll.objects.bulk_create(payrolls)


def remove_seeded_payroll(apps, schema_editor):
    Payroll = apps.get_model("hrm", "Payroll")
    Payroll.objects.filter(code__startswith="P7381").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0011_payroll"),
    ]

    operations = [
        migrations.RunPython(seed_payroll, remove_seeded_payroll),
    ]
