"""Add code, fees_group and is_active fields to FeesType, populating codes for existing rows."""
from django.db import migrations, models
import django.db.models.deletion


def assign_codes(apps, schema_editor):
    FeesType = apps.get_model("fees", "FeesType")
    counter = 80480
    for ft in FeesType.objects.order_by("id"):
        if not ft.code:
            counter += 1
            ft.code = f"FG{counter:05d}"
            ft.save(update_fields=["code"])


class Migration(migrations.Migration):

    dependencies = [
        ("fees", "0002_feesgroup_code_feesgroup_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="feestype",
            name="code",
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name="feestype",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="feestype",
            name="fees_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="fees_types",
                to="fees.feesgroup",
            ),
        ),
        migrations.RunPython(assign_codes, migrations.RunPython.noop),
    ]
