from django.contrib import admin

from apps.budgets.models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'budget_id',
        'budget_name',
        'user',
        'budget_scope',
        'category',
        'period_month',
        'period_year',
        'spending_limit',
        'warning_percent',
        'status',
    )
    list_filter = ('budget_scope', 'status', 'period_year', 'period_month')
    search_fields = ('budget_name', 'user__username', 'category__category_name')
    ordering = ('-period_year', '-period_month', 'budget_id')
