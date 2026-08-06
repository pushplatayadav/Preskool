from django.db import migrations

SAMPLE_TRANSACTIONS = [
    ("FT624893", "April Month Fees", "2024-04-25", "15000.00", "income", "cash", "completed"),
    ("FT624892", "Monthly Electricity", "2024-04-27", "1000.00", "expense", "credit", "completed"),
    ("FT624891", "Alumni Scholarship", "2024-05-03", "1000.00", "income", "cash", "pending"),
    ("FT624890", "AC Repair", "2024-05-15", "400.00", "expense", "cash", "completed"),
    ("FT624889", "Uniform Sales", "2024-05-20", "10500.00", "income", "credit", "completed"),
    ("FT624888", "Water Bill", "2024-06-06", "700.00", "expense", "cash", "pending"),
    ("FT624887", "Library Donation", "2024-06-18", "2000.00", "income", "cash", "completed"),
    ("FT624886", "Vehicle Repair", "2024-06-26", "800.00", "expense", "cash", "completed"),
    ("FT624885", "Cafeteria Income", "2024-07-08", "15000.00", "income", "credit", "completed"),
    ("FT624884", "Lab Equipments", "2024-07-10", "300.00", "expense", "cash", "completed"),
]


def seed_transactions(apps, schema_editor):
    Transaction = apps.get_model("finance", "Transaction")
    for txn_id, description, date, amount, transaction_type, payment_method, status in SAMPLE_TRANSACTIONS:
        Transaction.objects.get_or_create(
            transaction_id=txn_id,
            defaults={
                "description": description,
                "date": date,
                "amount": amount,
                "transaction_type": transaction_type,
                "payment_method": payment_method,
                "status": status,
            },
        )


def unseed_transactions(apps, schema_editor):
    Transaction = apps.get_model("finance", "Transaction")
    Transaction.objects.filter(transaction_id__in=[row[0] for row in SAMPLE_TRANSACTIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0007_add_transaction"),
    ]

    operations = [
        migrations.RunPython(seed_transactions, unseed_transactions),
    ]
