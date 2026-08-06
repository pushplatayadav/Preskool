from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0002_add_expense"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="expense_id",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
