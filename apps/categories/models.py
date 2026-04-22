from django.db import models

from apps.accounts.models import UserProfile


class ExpenseCategory(models.Model):
    TYPE_INCOME = 'income'
    TYPE_EXPENSE = 'expense'
    TYPE_BOTH = 'both'

    CATEGORY_TYPE_CHOICES = [
        (TYPE_INCOME, 'Thu nhập'),
        (TYPE_EXPENSE, 'Chi tiêu'),
        (TYPE_BOTH, 'Cả thu và chi'),
    ]

    category_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column='user_id',
        related_name='categories',
    )
    category_name = models.CharField(max_length=100)
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        default=TYPE_EXPENSE,
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    color_code = models.CharField(max_length=20, blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category_name'],
                name='uq_categories_user_name',
            ),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_categories_user_id'),
            models.Index(fields=['category_type'], name='idx_categories_category_type'),
            models.Index(fields=['is_default'], name='idx_categories_is_default'),
            models.Index(fields=['is_active'], name='idx_categories_is_active'),
        ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
