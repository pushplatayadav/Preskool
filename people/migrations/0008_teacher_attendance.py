from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_academicyear_id_alter_school_id"),
        ("people", "0007_staff_additional_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeacherAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late"), ("half_day", "Half Day"), ("holiday", "Holiday")], max_length=20)),
                ("remarks", models.TextField(blank=True)),
                ("academic_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.academicyear")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="people.teacher")),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("teacher", "date")},
            },
        ),
    ]
