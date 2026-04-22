from django.contrib import admin

from apps.debts.models import Debt, DebtPayment


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('debt_id', 'counterparty_name', 'debt_type', 'original_amount', 'remaining_amount', 'due_date', 'status')
    list_filter = ('debt_type', 'status', 'is_active')
    search_fields = ('counterparty_name', 'description')


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ('debt_payment_id', 'debt', 'amount', 'payment_date', 'bank_account')
    list_filter = ('payment_date',)
