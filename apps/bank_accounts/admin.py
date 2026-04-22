from django.contrib import admin

from apps.bank_accounts.models import BankAccount


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'bank_account_id',
        'account_name',
        'user',
        'account_type',
        'provider_name',
        'currency',
        'current_balance',
        'is_active',
    )
    list_filter = ('account_type', 'currency', 'is_active')
    search_fields = ('account_name', 'provider_name', 'account_number_masked', 'user__username')
    ordering = ('bank_account_id',)
