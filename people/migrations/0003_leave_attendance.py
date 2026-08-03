from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_student_additional_fields"),
        ("core", "0003_alter_academicyear_id_alter_school_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentLeave",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("leave_type", models.CharField(choices=[("medical", "Medical Leave"), ("casual", "Casual Leave"), ("maternity", "Maternity Leave"), ("paternity", "Paternity Leave"), ("special", "Special Leave")], max_length=20)),
                ("from_date", models.DateField()),
                ("to_date", models.DateField()),
                ("no_of_days", models.IntegerField(default=1)),
                ("leave_days_type", models.CharField(choices=[("full", "Full Day"), ("first_half", "First Half"), ("second_half", "Second Half")], default="full", max_length=20)),
                ("reason", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=20)),
                ("applied_on", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="leaves", to="people.student")),
            ],
            options={
                "ordering": ["-applied_on"],
            },
        ),
        migrations.CreateModel(
            name="StudentAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late"), ("half_day", "Half Day"), ("holiday", "Holiday")], max_length=20)),
                ("remarks", models.TextField(blank=True)),
                ("academic_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.academicyear")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="people.student")),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("student", "date")},
            },
        ),
    ]
