"""Add code and is_active fields to FeesGroup, populating codes for existing rows."""
from django.db import migrations, models


def assign_codes(apps, schema_editor):
    FeesGroup = apps.get_model("fees", "FeesGroup")
    counter = 80480
    for fg in FeesGroup.objects.order_by("id"):
        if not fg.code:
            counter += 1
            fg.code = f"FG{counter:05d}"
            fg.save(update_fields=["code"])


class Migration(migrations.Migration):

    dependencies = [
        ("fees", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="feesgroup",
            name="code",
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name="feesgroup",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(assign_codes, migrations.RunPython.noop),
    ]
