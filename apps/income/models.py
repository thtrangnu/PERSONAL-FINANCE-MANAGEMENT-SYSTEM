from django.db import models
from django.db.models import Q

from apps.accounts.models import UserProfile
from apps.bank_accounts.models import BankAccount
from apps.categories.models import ExpenseCategory


class Income(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_DELETED = 'deleted'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted'),
    ]

    income_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='incomes',
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        db_column='category_id',
        related_name='incomes',
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='bank_account_id',
        related_name='incomes',
    )
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    income_date = models.DateField()
    description = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incomes'
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name='chk_incomes_amount'),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_incomes_user_id'),
            models.Index(fields=['category'], name='idx_incomes_category_id'),
            models.Index(fields=['income_date'], name='idx_incomes_income_date'),
            models.Index(fields=['bank_account'], name='idx_incomes_bank_account_id'),
            models.Index(fields=['user', 'income_date'], name='idx_incomes_user_income_date'),
        ]
        verbose_name = 'income'
        verbose_name_plural = 'incomes'

    def __str__(self):
        return self.title
