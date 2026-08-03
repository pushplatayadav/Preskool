"""Seed initial leave requests for the Approve Request module."""
from datetime import date

from django.db import migrations


def seed_leave_requests(apps, schema_editor):
    LeaveRequest = apps.get_model("hrm", "LeaveRequest")
    if LeaveRequest.objects.exists():
        return

    rows = [
        {
            "code": "LR757001",
            "applicant_name": "James Deckar",
            "applicant_id": "9004",
            "role": "Student",
            "leave_type": "medical",
            "from_date": date(2024, 5, 5),
            "to_date": date(2024, 5, 7),
            "no_of_days": 5,
            "applied_on": date(2024, 5, 5),
            "authority": "Jacquelin",
            "status": "approved",
            "reason": "Headache & fever",
        },
        {
            "code": "LR757002",
            "applicant_name": "Richard",
            "applicant_id": "2145",
            "role": "Teacher",
            "leave_type": "casual",
            "from_date": date(2024, 5, 7),
            "to_date": date(2024, 5, 7),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 7),
            "authority": "Elizabeth",
            "status": "approved",
            "reason": "Personal work",
        },
        {
            "code": "LR757003",
            "applicant_name": "Susan",
            "applicant_id": "4147",
            "role": "Admin",
            "leave_type": "maternity",
            "from_date": date(2024, 5, 8),
            "to_date": date(2024, 5, 19),
            "no_of_days": 10,
            "applied_on": date(2024, 5, 2),
            "authority": "Teresa",
            "status": "approved",
            "reason": "Maternity leave",
        },
        {
            "code": "LR757004",
            "applicant_name": "Lisa",
            "applicant_id": "2145",
            "role": "Librarian",
            "leave_type": "sick",
            "from_date": date(2024, 5, 5),
            "to_date": date(2024, 5, 7),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 4),
            "authority": "Edward",
            "status": "approved",
            "reason": "Fever",
        },
        {
            "code": "LR757005",
            "applicant_name": "Janet",
            "applicant_id": "1457",
            "role": "Driver",
            "leave_type": "paternity",
            "from_date": date(2024, 5, 7),
            "to_date": date(2024, 5, 7),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 6),
            "authority": "Daniel",
            "status": "disapproved",
            "reason": "Paternity leave",
        },
        {
            "code": "LR757006",
            "applicant_name": "Ryan",
            "applicant_id": "9784",
            "role": "Student",
            "leave_type": "special",
            "from_date": date(2024, 5, 8),
            "to_date": date(2024, 5, 19),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 12),
            "authority": "Hellana",
            "status": "pending",
            "reason": "Family function",
        },
        {
            "code": "LR757007",
            "applicant_name": "Gifford",
            "applicant_id": "7457",
            "role": "Student",
            "leave_type": "medical",
            "from_date": date(2024, 5, 7),
            "to_date": date(2024, 5, 7),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 4),
            "authority": "Erickson",
            "status": "pending",
            "reason": "Cold & cough",
        },
        {
            "code": "LR757008",
            "applicant_name": "Julie",
            "applicant_id": "4655",
            "role": "Student",
            "leave_type": "casual",
            "from_date": date(2024, 5, 5),
            "to_date": date(2024, 5, 7),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 4),
            "authority": "Raul",
            "status": "approved",
            "reason": "Personal work",
        },
        {
            "code": "LR757009",
            "applicant_name": "Joann",
            "applicant_id": "4178",
            "role": "Student",
            "leave_type": "medical",
            "from_date": date(2024, 5, 8),
            "to_date": date(2024, 5, 19),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 4),
            "authority": "Aaron",
            "status": "pending",
            "reason": "Doctor appointment",
        },
        {
            "code": "LR757010",
            "applicant_name": "Kathleen",
            "applicant_id": "5898",
            "role": "Student",
            "leave_type": "casual",
            "from_date": date(2024, 5, 7),
            "to_date": date(2024, 5, 7),
            "no_of_days": 1,
            "applied_on": date(2024, 5, 4),
            "authority": "Morgan",
            "status": "pending",
            "reason": "Family function",
        },
    ]

    for row in rows:
        LeaveRequest.objects.create(**row)


def unseed_leave_requests(apps, schema_editor):
    LeaveRequest = apps.get_model("hrm", "LeaveRequest")
    LeaveRequest.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0005_leaverrequest"),
    ]

    operations = [
        migrations.RunPython(seed_leave_requests, unseed_leave_requests),
    ]
