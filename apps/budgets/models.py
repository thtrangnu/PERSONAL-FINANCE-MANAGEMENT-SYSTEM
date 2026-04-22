from django.db import models
from django.db.models import Q

from apps.accounts.models import UserProfile
from apps.categories.models import ExpenseCategory


class Budget(models.Model):
    SCOPE_OVERALL = 'overall'
    SCOPE_CATEGORY = 'category'

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CLOSED = 'closed'

    SCOPE_CHOICES = [
        (SCOPE_OVERALL, 'Ngân sách tổng'),
        (SCOPE_CATEGORY, 'Theo danh mục'),
    ]

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Đang dùng'),
        (STATUS_INACTIVE, 'Tạm tắt'),
        (STATUS_CLOSED, 'Đã đóng'),
    ]

    budget_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='budgets',
    )
    budget_name = models.CharField(max_length=120)
    budget_scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        db_column='category_id',
        related_name='budgets',
    )
    period_month = models.PositiveSmallIntegerField()
    period_year = models.PositiveSmallIntegerField()
    spending_limit = models.DecimalField(max_digits=18, decimal_places=2)
    warning_percent = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'
        constraints = [
            models.CheckConstraint(
                condition=Q(period_month__gte=1) & Q(period_month__lte=12),
                name='chk_budgets_period_month',
            ),
            models.CheckConstraint(
                condition=Q(spending_limit__gt=0),
                name='chk_budgets_spending_limit',
            ),
            models.CheckConstraint(
                condition=Q(warning_percent__gt=0) & Q(warning_percent__lte=100),
                name='chk_budgets_warning_percent',
            ),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_budgets_user_id'),
            models.Index(fields=['category'], name='idx_budgets_category_id'),
            models.Index(fields=['period_year', 'period_month'], name='idx_budgets_period_year_month'),
            models.Index(
                fields=['user', 'period_year', 'period_month'],
                name='idx_budgets_user_year_month',
            ),
        ]
        verbose_name = 'budget'
        verbose_name_plural = 'budgets'

    def __str__(self):
        return self.budget_name
