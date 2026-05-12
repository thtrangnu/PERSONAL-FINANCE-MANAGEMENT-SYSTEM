from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.expenses.models import Expense
from apps.sharing.models import GroupMember, SharedTransaction, SharingGroup
from apps.tests.support import create_bank_account, create_category, create_user_pair


class SharingFlowTests(TestCase):
    def setUp(self):
        self.owner_auth_user, self.owner_profile = create_user_pair()
        self.member_auth_user, self.member_profile = create_user_pair(
            username='member',
            email='member@example.com',
        )
        self.outsider_auth_user, self.outsider_profile = create_user_pair(
            username='outsider',
            email='outsider@example.com',
        )
        self.group = SharingGroup.objects.create(
            owner_user=self.owner_profile,
            group_name='Nhóm gia đình',
            description='Chi tiêu chung',
        )
        GroupMember.objects.create(
            group=self.group,
            user=self.owner_profile,
            member_role=GroupMember.ROLE_OWNER,
            status=GroupMember.STATUS_ACTIVE,
        )

    def test_non_member_cannot_access_group_detail(self):
        self.client.force_login(self.outsider_auth_user)

        response = self.client.get(reverse('sharing_group_detail', args=[self.group.group_id]))

        self.assertEqual(response.status_code, 404)

    def test_owner_can_toggle_group_status(self):
        self.client.force_login(self.owner_auth_user)

        response = self.client.post(
            reverse('sharing_group_toggle_status', args=[self.group.group_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.status, SharingGroup.STATUS_INACTIVE)
        self.assertEqual(response.json()['label'], 'Tạm tắt')

    def test_non_owner_cannot_toggle_group_status(self):
        GroupMember.objects.create(
            group=self.group,
            user=self.member_profile,
            member_role=GroupMember.ROLE_MEMBER,
            status=GroupMember.STATUS_ACTIVE,
        )
        self.client.force_login(self.member_auth_user)

        response = self.client.post(reverse('sharing_group_toggle_status', args=[self.group.group_id]))

        self.assertEqual(response.status_code, 404)

    def test_active_member_can_share_own_expense_into_group(self):
        GroupMember.objects.create(
            group=self.group,
            user=self.member_profile,
            member_role=GroupMember.ROLE_MEMBER,
            status=GroupMember.STATUS_ACTIVE,
        )
        category = create_category(self.member_profile, name='Ăn chung')
        account = create_bank_account(self.member_profile, name='Ví thành viên', balance='400')
        expense = Expense.objects.create(
            user=self.member_profile,
            category=category,
            bank_account=account,
            amount=Decimal('120'),
            expense_date=timezone.now().date(),
            status=Expense.STATUS_ACTIVE,
        )

        self.client.force_login(self.member_auth_user)
        response = self.client.post(
            reverse('shared_transaction_create', args=[self.group.group_id]),
            {
                'expense': expense.expense_id,
                'income': '',
                'note': 'Chia sẻ bữa tối',
            },
        )

        self.assertRedirects(response, reverse('sharing_group_detail', args=[self.group.group_id]))

        shared_record = SharedTransaction.objects.get(group=self.group, shared_by_user=self.member_profile)
        self.assertEqual(shared_record.expense_id, expense.expense_id)
        self.assertIsNone(shared_record.income_id)
        self.assertEqual(shared_record.note, 'Chia sẻ bữa tối')
