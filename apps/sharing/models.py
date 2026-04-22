from django.db import models

from apps.accounts.models import UserProfile
from apps.expenses.models import Expense
from apps.income.models import Income


class SharingGroup(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Đang dùng'),
        (STATUS_INACTIVE, 'Tạm tắt'),
        (STATUS_ARCHIVED, 'Đã lưu trữ'),
    ]

    group_id = models.BigAutoField(primary_key=True)
    owner_user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        db_column='owner_user_id',
        related_name='owned_groups',
    )
    group_name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups'
        indexes = [
            models.Index(fields=['owner_user'], name='idx_groups_owner_user_id'),
            models.Index(fields=['status'], name='idx_groups_status'),
        ]

    def __str__(self):
        return self.group_name


class GroupMember(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_MEMBER = 'member'
    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_LEFT = 'left'
    STATUS_REMOVED = 'removed'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Chủ nhóm'),
        (ROLE_MEMBER, 'Thành viên'),
    ]
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Chờ xác nhận'),
        (STATUS_ACTIVE, 'Đang tham gia'),
        (STATUS_LEFT, 'Đã rời'),
        (STATUS_REMOVED, 'Đã xóa'),
    ]

    group_member_id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(SharingGroup, on_delete=models.CASCADE, db_column='group_id', related_name='members')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id', related_name='group_memberships')
    member_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        db_table = 'group_members'
        constraints = [
            models.UniqueConstraint(fields=['group', 'user'], name='uq_group_members_group_user'),
        ]
        indexes = [
            models.Index(fields=['group'], name='idx_group_members_group_id'),
            models.Index(fields=['user'], name='idx_group_members_user_id'),
            models.Index(fields=['status'], name='idx_group_members_status'),
        ]

    def __str__(self):
        return f'{self.group} - {self.user}'


class SharedTransaction(models.Model):
    VISIBILITY_VISIBLE = 'visible'
    VISIBILITY_HIDDEN = 'hidden'

    VISIBILITY_CHOICES = [
        (VISIBILITY_VISIBLE, 'Đang hiển thị'),
        (VISIBILITY_HIDDEN, 'Đã ẩn'),
    ]

    shared_transaction_id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(SharingGroup, on_delete=models.CASCADE, db_column='group_id', related_name='shared_transactions')
    shared_by_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='shared_by_user_id', related_name='shared_transactions')
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, blank=True, null=True, db_column='expense_id', related_name='shared_records')
    income = models.ForeignKey(Income, on_delete=models.CASCADE, blank=True, null=True, db_column='income_id', related_name='shared_records')
    visibility_status = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default=VISIBILITY_VISIBLE)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shared_transactions'
        indexes = [
            models.Index(fields=['group'], name='idx_shared_tx_group'),
            models.Index(fields=['shared_by_user'], name='idx_shared_tx_user'),
            models.Index(fields=['expense'], name='idx_shared_tx_expense'),
            models.Index(fields=['income'], name='idx_shared_tx_income'),
        ]

    def __str__(self):
        return f'{self.group} shared transaction'
