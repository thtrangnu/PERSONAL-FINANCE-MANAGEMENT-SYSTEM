from django.contrib import admin

from apps.expenses.models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'expense_id',
        'user',
        'category',
        'bank_account',
        'amount',
        'expense_date',
        'payment_method',
        'status',
    )
    list_filter = ('status', 'category', 'payment_method', 'expense_date')
    search_fields = ('description', 'note', 'user__username')
    date_hierarchy = 'expense_date'
    ordering = ('-expense_date', '-expense_id')
