from django.db import models

from apps.accounts.models import UserProfile


class BankAccount(models.Model):
    TYPE_BANK = 'bank'
    TYPE_CASH = 'cash'
    TYPE_E_WALLET = 'e_wallet'
    TYPE_OTHER = 'other'

    ACCOUNT_TYPE_CHOICES = [
        (TYPE_BANK, 'Tài khoản ngân hàng'),
        (TYPE_CASH, 'Tiền mặt'),
        (TYPE_E_WALLET, 'Ví điện tử'),
        (TYPE_OTHER, 'Khác'),
    ]

    bank_account_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='bank_accounts',
    )
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    provider_name = models.CharField(max_length=100, blank=True, null=True)
    account_number_masked = models.CharField(max_length=30, blank=True, null=True)
    currency = models.CharField(max_length=10, default='VND')
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bank_accounts'
        indexes = [
            models.Index(fields=['user'], name='idx_bank_accounts_user_id'),
            models.Index(fields=['account_type'], name='idx_bank_accounts_account_type'),
            models.Index(fields=['is_active'], name='idx_bank_accounts_is_active'),
        ]
        verbose_name = 'bank account'
        verbose_name_plural = 'bank accounts'

    def __str__(self):
        return self.account_name
