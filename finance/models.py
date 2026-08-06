from decimal import Decimal

from django.db import models

_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]
_TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety",
]
_SCALES = ["", "Thousand", "Million", "Billion", "Trillion"]


def _number_to_words(value):
    if value is None:
        return "Zero"
    try:
        value = Decimal(str(value))
    except Exception:
        return "Zero"
    if value < 0:
        return "Minus " + _number_to_words(-value)

    whole = int(value)
    cents = int((value - whole) * 100 + Decimal("0.5"))

    if whole == 0:
        words = "Zero"
    else:
        parts = []
        scale_index = 0
        while whole > 0:
            chunk = whole % 1000
            if chunk:
                chunk_words = []
                hundreds = chunk // 100
                remainder = chunk % 100
                if hundreds:
                    chunk_words.append(_ONES[hundreds] + " Hundred")
                if remainder:
                    if remainder < 20:
                        chunk_words.append(_ONES[remainder])
                    else:
                        chunk_words.append(_TENS[remainder // 10] + ((" " + _ONES[remainder % 10]) if remainder % 10 else ""))
                if scale_index:
                    chunk_words.append(_SCALES[scale_index])
                parts.insert(0, " ".join(chunk_words))
            whole //= 1000
            scale_index += 1
        words = " ".join(parts)

    if cents:
        words += " and " + ("0" if cents < 10 else "") + str(cents) + "/100"
    return words


class Income(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("credit", "Credit"),
    ]
    SOURCE_CHOICES = [
        ("tuition_fees", "Tuition Fees"),
        ("government_grants", "Government Grants"),
        ("donations", "Donations"),
        ("merchandise", "Merchandise"),
        ("parking_fees", "Parking Fees"),
        ("sports", "Sports"),
        ("book_fair", "Book Fair"),
        ("cafeteria", "Cafeteria"),
        ("other", "Other"),
    ]

    income_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    income_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="other")
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHOD_CHOICES, default="cash"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Income"
        verbose_name_plural = "Incomes"

    def __str__(self):
        return f"{self.income_name} ({self.income_id or self.invoice_number})"

    @property
    def amount_display(self):
        formatted = f"{self.amount:,.2f}"
        if formatted.endswith(".00"):
            return f"{formatted[:-3]}"
        return f"{formatted}"

    def save(self, *args, **kwargs):
        if not self.income_id:
            numbers = []
            for inc in Income.objects.exclude(income_id="").exclude(pk=self.pk):
                if inc.income_id and inc.income_id.startswith("I") and inc.income_id[1:].isdigit():
                    numbers.append(int(inc.income_id[1:]))
            candidate = max(numbers) + 1 if numbers else 639248
            while Income.objects.filter(income_id=f"I{candidate}").exists():
                candidate += 1
            self.income_id = f"I{candidate}"
        if not self.invoice_number:
            numbers = []
            for inc in Income.objects.exclude(invoice_number="").exclude(pk=self.pk):
                if inc.invoice_number and inc.invoice_number.startswith("INV") and inc.invoice_number[3:].isdigit():
                    numbers.append(int(inc.invoice_number[3:]))
            candidate = max(numbers) + 1 if numbers else 681537
            while Income.objects.filter(invoice_number=f"INV{candidate}").exists():
                candidate += 1
            self.invoice_number = f"INV{candidate}"
        super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
    category_id = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "category_id"]
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return f"{self.name} ({self.category_id})"

    def save(self, *args, **kwargs):
        if not self.category_id:
            numbers = []
            for cat in ExpenseCategory.objects.exclude(category_id="").exclude(pk=self.pk):
                if cat.category_id and cat.category_id.startswith("EXC") and cat.category_id[3:].isdigit():
                    numbers.append(int(cat.category_id[3:]))
            candidate = max(numbers) + 1 if numbers else 617453
            while ExpenseCategory.objects.filter(category_id=f"EXC{candidate}").exists():
                candidate += 1
            self.category_id = f"EXC{candidate}"
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank_transfer", "Bank Transfer"),
        ("credit_card", "Credit Card"),
        ("cheque", "Cheque"),
        ("online", "Online"),
    ]
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled"),
    ]

    expense_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    expense_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHOD_CHOICES, default="cash"
    )
    date = models.DateField()
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid")
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.expense_name} ({self.expense_id or self.invoice_number})"

    @property
    def amount_display(self):
        formatted = f"{self.amount:,.2f}"
        if formatted.endswith(".00"):
            return f"{formatted[:-3]}"
        return f"{formatted}"

    def save(self, *args, **kwargs):
        if not self.expense_id:
            numbers = []
            for exp in Expense.objects.exclude(expense_id="").exclude(pk=self.pk):
                if exp.expense_id and exp.expense_id.startswith("EX") and exp.expense_id[2:].isdigit():
                    numbers.append(int(exp.expense_id[2:]))
            candidate = max(numbers) + 1 if numbers else 628148
            while Expense.objects.filter(expense_id=f"EX{candidate}").exists():
                candidate += 1
            self.expense_id = f"EX{candidate}"
        if not self.invoice_number:
            numbers = []
            for exp in Expense.objects.exclude(invoice_number="").exclude(pk=self.pk):
                if exp.invoice_number and exp.invoice_number.startswith("INV") and exp.invoice_number[3:].isdigit():
                    numbers.append(int(exp.invoice_number[3:]))
            candidate = max(numbers) + 1 if numbers else 681537
            while Expense.objects.filter(invoice_number=f"INV{candidate}").exists():
                candidate += 1
            self.invoice_number = f"INV{candidate}"
        super().save(*args, **kwargs)


class Invoice(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("credit", "Credit"),
        ("bank_transfer", "Bank Transfer"),
        ("online", "Online"),
        ("cheque", "Cheque"),
    ]
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("overdue", "Overdue"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    student_name = models.CharField(max_length=200, default="")
    student_id = models.CharField(max_length=50, blank=True, default="")
    term = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    bill_to_address = models.TextField(blank=True, default="")
    bill_to_email = models.EmailField(blank=True, default="")
    bill_to_phone = models.CharField(max_length=30, blank=True, default="")
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHOD_CHOICES, default="cash"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    terms = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    signature_name = models.CharField(max_length=200, blank=True, default="")
    company_logo = models.ImageField(upload_to="invoices/logos/", blank=True, null=True)
    signature = models.ImageField(upload_to="invoices/signatures/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.invoice_number} - {self.student_name}"

    @property
    def amount_display(self):
        formatted = f"{self.amount:,.2f}"
        if formatted.endswith(".00"):
            return f"{formatted[:-3]}"
        return f"{formatted}"

    @property
    def subtotal(self):
        if self.items.exists():
            return sum((item.amount for item in self.items.all()), Decimal("0"))
        return self.amount or Decimal("0")

    @property
    def discount_amount(self):
        return (self.subtotal * self.discount) / Decimal("100")

    @property
    def tax_amount(self):
        net = self.subtotal - self.discount_amount
        return (net * self.tax) / Decimal("100")

    @property
    def payable_amount(self):
        net = self.subtotal - self.discount_amount
        return net + self.tax_amount

    @property
    def payable_display(self):
        formatted = f"{self.payable_amount:,.2f}"
        if formatted.endswith(".00"):
            return f"{formatted[:-3]}"
        return f"{formatted}"

    @property
    def payable_in_words(self):
        return _number_to_words(self.payable_amount)

    @property
    def subtotal_display(self):
        return f"{self.subtotal:,.2f}"

    @property
    def discount_amount_display(self):
        return f"{self.discount_amount:,.2f}"

    @property
    def tax_amount_display(self):
        return f"{self.tax_amount:,.2f}"

    @property
    def payable_amount_display(self):
        return f"{self.payable_amount:,.2f}"

    @property
    def items_json(self):
        import json

        return json.dumps([
            {
                "description": item.description,
                "due_date": item.due_date.strftime("%d %b %Y") if item.due_date else "",
                "amount": item.amount_display,
            }
            for item in self.items.all()
        ])

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            numbers = []
            for inv in Invoice.objects.exclude(invoice_number="").exclude(pk=self.pk):
                if inv.invoice_number and inv.invoice_number.startswith("INV") and inv.invoice_number[3:].isdigit():
                    numbers.append(int(inv.invoice_number[3:]))
            candidate = max(numbers) + 1 if numbers else 681537
            while Invoice.objects.filter(invoice_number=f"INV{candidate}").exists():
                candidate += 1
            self.invoice_number = f"INV{candidate}"
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items",
    )
    description = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

    @property
    def amount_display(self):
        formatted = f"{self.amount:,.2f}"
        if formatted.endswith(".00"):
            return f"{formatted[:-3]}"
        return f"{formatted}"

    @property
    def net_amount(self):
        net = (Decimal(self.quantity) * self.unit_price)
        if self.discount_percent:
            net = net * (Decimal("1") - self.discount_percent / Decimal("100"))
        return net.quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        if self.unit_price == 0 and self.amount and self.amount != 0:
            self.unit_price = self.amount / max(self.quantity or 1, 1)
        self.amount = self.net_amount
        super().save(*args, **kwargs)


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("credit", "Credit"),
    ]
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("pending", "Pending"),
    ]

    transaction_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.CharField(max_length=255)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES, default="income"
    )
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHOD_CHOICES, default="cash"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.description} ({self.transaction_id})"

    @property
    def amount_display(self):
        formatted = f"{self.amount:,.2f}"
        if formatted.endswith(".00"):
            return f"{formatted[:-3]}"
        return f"{formatted}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            numbers = []
            for txn in Transaction.objects.exclude(transaction_id="").exclude(pk=self.pk):
                if txn.transaction_id and txn.transaction_id.startswith("FT") and txn.transaction_id[2:].isdigit():
                    numbers.append(int(txn.transaction_id[2:]))
            candidate = max(numbers) + 1 if numbers else 624893
            while Transaction.objects.filter(transaction_id=f"FT{candidate}").exists():
                candidate += 1
            self.transaction_id = f"FT{candidate}"
        super().save(*args, **kwargs)
