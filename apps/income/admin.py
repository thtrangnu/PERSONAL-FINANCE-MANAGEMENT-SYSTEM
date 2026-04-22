from django.contrib import admin

from apps.income.models import Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        'income_id',
        'title',
        'user',
        'category',
        'bank_account',
        'amount',
        'income_date',
        'status',
    )
    list_filter = ('status', 'category', 'income_date')
    search_fields = ('title', 'description', 'note', 'user__username')
    date_hierarchy = 'income_date'
    ordering = ('-income_date', '-income_id')
