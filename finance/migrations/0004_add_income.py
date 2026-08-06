from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0003_add_expense_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Income",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("income_id", models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ("invoice_number", models.CharField(blank=True, max_length=50, unique=True)),
                ("income_name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("source", models.CharField(choices=[("tuition_fees", "Tuition Fees"), ("government_grants", "Government Grants"), ("donations", "Donations"), ("merchandise", "Merchandise"), ("parking_fees", "Parking Fees"), ("sports", "Sports"), ("book_fair", "Book Fair"), ("cafeteria", "Cafeteria"), ("other", "Other")], default="other", max_length=50)),
                ("date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("payment_method", models.CharField(choices=[("cash", "Cash"), ("credit", "Credit")], default="cash", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Income",
                "verbose_name_plural": "Incomes",
                "ordering": ["-date", "-created_at"],
            },
        ),
    ]
