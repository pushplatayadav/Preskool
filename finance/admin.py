from django.contrib import admin

from .models import Expense, ExpenseCategory, Income, Invoice, InvoiceItem, Product, Transaction


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("income_id", "income_name", "source", "date", "amount", "payment_method")
    list_filter = ("source", "payment_method", "date")
    search_fields = ("income_id", "invoice_number", "income_name", "description")
    ordering = ("-date", "-created_at")


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "name", "description", "created_at")
    search_fields = ("category_id", "name", "description")
    ordering = ("category_id",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("expense_id", "expense_name", "category", "date", "amount", "payment_method", "status")
    list_filter = ("status", "payment_method", "category", "date")
    search_fields = ("expense_id", "invoice_number", "expense_name", "description")
    ordering = ("-date", "-created_at")


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "unit_price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "student_name", "date", "due_date", "amount", "payment_method", "status")
    list_filter = ("status", "payment_method", "date")
    search_fields = ("invoice_number", "student_name", "student_id", "description")
    ordering = ("-date", "-created_at")
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "product", "description", "quantity", "unit_price", "discount_percent", "amount")
    search_fields = ("invoice__invoice_number", "description", "product__name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "description", "date", "amount", "transaction_type", "payment_method", "status")
    list_filter = ("transaction_type", "payment_method", "status", "date")
    search_fields = ("transaction_id", "description")
    ordering = ("-date", "-created_at")
