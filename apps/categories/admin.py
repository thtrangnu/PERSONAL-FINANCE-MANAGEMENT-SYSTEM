from django.contrib import admin

from apps.categories.models import ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'category_type', 'user', 'is_default', 'is_active')
    list_filter = ('category_type', 'is_default', 'is_active')
    search_fields = ('category_name', 'description')
    ordering = ('category_id',)
