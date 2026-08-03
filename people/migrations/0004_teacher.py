from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0015_alter_examattendance_student_and_more"),
        ("people", "0003_leave_attendance"),
        ("accounts", "0002_user_is_email_verified_otpverification"),
    ]

    operations = [
        migrations.CreateModel(
            name="Teacher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("teacher_id", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("date_of_join", models.DateField(blank=True, null=True)),
                ("gender", models.CharField(choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], default="male", max_length=10)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("profile_image", models.ImageField(blank=True, null=True, upload_to="teachers/")),
                ("status", models.CharField(choices=[("active", "Active"), ("inactive", "Inactive")], default="active", max_length=10)),
                ("address", models.TextField(blank=True)),
                ("qualification", models.CharField(blank=True, max_length=200)),
                ("experience", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("school_class", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="teachers", to="academics.schoolclass")),
                ("subject", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="teachers", to="academics.subject")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="teacher_profiles", to="accounts.user")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
