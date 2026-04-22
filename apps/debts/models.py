from django.db import models
from django.db.models import Q

from apps.accounts.models import UserProfile
from apps.bank_accounts.models import BankAccount


class Debt(models.Model):
    TYPE_I_OWE = 'i_owe'
    TYPE_OWED_TO_ME = 'owed_to_me'

    STATUS_PENDING = 'pending'
    STATUS_PARTIALLY_PAID = 'partially_paid'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'

    DEBT_TYPE_CHOICES = [
        (TYPE_I_OWE, 'Mình nợ'),
        (TYPE_OWED_TO_ME, 'Người khác nợ mình'),
    ]
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Đang theo dõi'),
        (STATUS_PARTIALLY_PAID, 'Đã trả một phần'),
        (STATUS_PAID, 'Đã trả xong'),
        (STATUS_OVERDUE, 'Quá hạn'),
    ]

    debt_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id', related_name='debts')
    debt_type = models.CharField(max_length=20, choices=DEBT_TYPE_CHOICES)
    counterparty_name = models.CharField(max_length=150)
    original_amount = models.DecimalField(max_digits=18, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=18, decimal_places=2)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    description = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'debts'
        constraints = [
            models.CheckConstraint(condition=Q(original_amount__gt=0), name='chk_debts_original_amount'),
            models.CheckConstraint(condition=Q(remaining_amount__gte=0), name='chk_debts_remaining_amount'),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_debts_user_id'),
            models.Index(fields=['status'], name='idx_debts_status'),
            models.Index(fields=['due_date'], name='idx_debts_due_date'),
            models.Index(fields=['user', 'status', 'due_date'], name='idx_debts_user_status_due'),
        ]

    def __str__(self):
        return f'{self.counterparty_name} - {self.original_amount}'


class DebtPayment(models.Model):
    debt_payment_id = models.BigAutoField(primary_key=True)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, db_column='debt_id', related_name='payments')
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='bank_account_id',
        related_name='debt_payments',
    )
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debt_payments'
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name='chk_debt_payments_amount'),
        ]
        indexes = [
            models.Index(fields=['debt'], name='idx_debt_payments_debt_id'),
            models.Index(fields=['payment_date'], name='idx_debt_payments_date'),
            models.Index(fields=['bank_account'], name='idx_debt_payments_account'),
        ]

    def __str__(self):
        return f'{self.amount} - {self.payment_date}'
