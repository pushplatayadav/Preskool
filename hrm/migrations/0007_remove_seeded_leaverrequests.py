"""Remove the seeded demo leave requests from the Approve Request module."""
from django.db import migrations

SEEDED_CODES = [
    "LR757001",
    "LR757002",
    "LR757003",
    "LR757004",
    "LR757005",
    "LR757006",
    "LR757007",
    "LR757008",
    "LR757009",
    "LR757010",
]


def remove_seeded_leave_requests(apps, schema_editor):
    LeaveRequest = apps.get_model("hrm", "LeaveRequest")
    LeaveRequest.objects.filter(code__in=SEEDED_CODES).delete()


def restore_seeded_leave_requests(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0006_seed_leaverrequests"),
    ]

    operations = [
        migrations.RunPython(
            remove_seeded_leave_requests,
            restore_seeded_leave_requests,
        ),
    ]
