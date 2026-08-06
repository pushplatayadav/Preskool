import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0005_add_invoice"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("unit_price", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
        migrations.AddField(
            model_name="invoice",
            name="company_logo",
            field=models.ImageField(blank=True, null=True, upload_to="invoices/logos/"),
        ),
        migrations.AddField(
            model_name="invoice",
            name="notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="invoice",
            name="signature",
            field=models.ImageField(blank=True, null=True, upload_to="invoices/signatures/"),
        ),
        migrations.AddField(
            model_name="invoice",
            name="signature_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="invoiceitem",
            name="discount_percent",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name="invoiceitem",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="items",
                to="finance.product",
            ),
        ),
        migrations.AddField(
            model_name="invoiceitem",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="invoiceitem",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
