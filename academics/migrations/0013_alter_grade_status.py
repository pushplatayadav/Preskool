from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("academics", "0012_exam_grade_examschedule_examattendance_examresult"),
    ]

    operations = [
        migrations.AddField(
            model_name="grade",
            name="status",
            field=models.CharField(
                choices=[("active", "Active"), ("inactive", "Inactive")],
                default="active",
                max_length=10,
            ),
        ),
    ]
