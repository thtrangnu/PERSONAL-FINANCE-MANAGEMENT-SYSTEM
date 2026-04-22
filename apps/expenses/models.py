from django.db import models
from django.db.models import Q

from apps.accounts.models import UserProfile
from apps.bank_accounts.models import BankAccount
from apps.categories.models import ExpenseCategory


class Expense(models.Model):
    METHOD_CASH = 'cash'
    METHOD_BANK = 'bank'
    METHOD_E_WALLET = 'e_wallet'
    METHOD_CREDIT_CARD = 'credit_card'
    METHOD_OTHER = 'other'

    STATUS_ACTIVE = 'active'
    STATUS_DELETED = 'deleted'

    PAYMENT_METHOD_CHOICES = [
        (METHOD_CASH, 'Cash'),
        (METHOD_BANK, 'Bank'),
        (METHOD_E_WALLET, 'E-wallet'),
        (METHOD_CREDIT_CARD, 'Credit card'),
        (METHOD_OTHER, 'Other'),
    ]

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted'),
    ]

    expense_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='expenses',
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        db_column='category_id',
        related_name='expenses',
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='bank_account_id',
        related_name='expenses',
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    expense_date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name='chk_expenses_amount'),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_expenses_user_id'),
            models.Index(fields=['category'], name='idx_expenses_category_id'),
            models.Index(fields=['bank_account'], name='idx_expenses_bank_account_id'),
            models.Index(fields=['expense_date'], name='idx_expenses_expense_date'),
            models.Index(fields=['user', 'expense_date'], name='idx_expenses_user_expense_date'),
            models.Index(
                fields=['user', 'category', 'expense_date'],
                name='idx_exp_user_cat_date',
            ),
        ]
        verbose_name = 'expense'
        verbose_name_plural = 'expenses'

    def __str__(self):
        return f'{self.amount} on {self.expense_date}'
