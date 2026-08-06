from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0004_add_income"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(blank=True, max_length=50, unique=True)),
                ("student_name", models.CharField(default="", max_length=200)),
                ("student_id", models.CharField(blank=True, default="", max_length=50)),
                ("term", models.CharField(blank=True, default="", max_length=100)),
                ("description", models.TextField(blank=True, default="")),
                ("bill_to_address", models.TextField(blank=True, default="")),
                ("bill_to_email", models.EmailField(blank=True, default="", max_length=254)),
                ("bill_to_phone", models.CharField(blank=True, default="", max_length=30)),
                ("date", models.DateField()),
                ("due_date", models.DateField(blank=True, null=True)),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("discount", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("tax", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("payment_method", models.CharField(choices=[("cash", "Cash"), ("credit", "Credit"), ("bank_transfer", "Bank Transfer"), ("online", "Online"), ("cheque", "Cheque")], default="cash", max_length=30)),
                ("status", models.CharField(choices=[("paid", "Paid"), ("pending", "Pending"), ("overdue", "Overdue")], default="pending", max_length=20)),
                ("terms", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Invoice",
                "verbose_name_plural": "Invoices",
                "ordering": ["-date", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="InvoiceItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=255)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="finance.invoice")),
            ],
            options={
                "verbose_name": "Invoice Item",
                "verbose_name_plural": "Invoice Items",
                "ordering": ["id"],
            },
        ),
    ]
