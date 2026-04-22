from django.db import models

from apps.accounts.models import UserProfile
from apps.budgets.models import Budget
from apps.expenses.models import Expense


class Alert(models.Model):
    TYPE_BUDGET_WARNING = 'budget_warning'
    TYPE_BUDGET_EXCEEDED = 'budget_exceeded'
    TYPE_DEBT_OVERDUE = 'debt_overdue'
    TYPE_SYSTEM_INFO = 'system_info'
    TYPE_OTHER = 'other'

    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_CRITICAL = 'critical'

    ALERT_TYPE_CHOICES = [
        (TYPE_BUDGET_WARNING, 'Cảnh báo ngân sách'),
        (TYPE_BUDGET_EXCEEDED, 'Vượt ngân sách'),
        (TYPE_DEBT_OVERDUE, 'Nợ quá hạn'),
        (TYPE_SYSTEM_INFO, 'Thông tin hệ thống'),
        (TYPE_OTHER, 'Khác'),
    ]

    SEVERITY_CHOICES = [
        (SEVERITY_INFO, 'Thông tin'),
        (SEVERITY_WARNING, 'Cần chú ý'),
        (SEVERITY_CRITICAL, 'Nghiêm trọng'),
    ]

    alert_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='alerts',
    )
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=150)
    message = models.TextField()
    related_budget = models.ForeignKey(
        Budget,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='related_budget_id',
        related_name='alerts',
    )
    related_expense = models.ForeignKey(
        Expense,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='related_expense_id',
        related_name='alerts',
    )
    related_debt_id = models.PositiveBigIntegerField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['user'], name='idx_alerts_user_id'),
            models.Index(fields=['alert_type'], name='idx_alerts_alert_type'),
            models.Index(fields=['is_read'], name='idx_alerts_is_read'),
            models.Index(fields=['created_at'], name='idx_alerts_created_at'),
            models.Index(fields=['user', 'is_read', 'created_at'], name='idx_alerts_user_read_at'),
        ]
        verbose_name = 'alert'
        verbose_name_plural = 'alerts'

    def __str__(self):
        return self.title
