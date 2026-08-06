from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0006_invoice_extras_product_invoiceitem_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_id", models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ("description", models.CharField(max_length=255)),
                ("date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("transaction_type", models.CharField(choices=[("income", "Income"), ("expense", "Expense")], default="income", max_length=20)),
                ("payment_method", models.CharField(choices=[("cash", "Cash"), ("credit", "Credit")], default="cash", max_length=30)),
                ("status", models.CharField(choices=[("completed", "Completed"), ("pending", "Pending")], default="completed", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
                "ordering": ["-date", "-created_at"],
            },
        ),
    ]
