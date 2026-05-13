from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.alerts.models import Alert
from apps.debts.models import Debt
from apps.tests.support import create_bank_account, create_user_pair


class DebtFlowTests(TestCase):
    def setUp(self):
        self.auth_user, self.profile = create_user_pair()
        self.client.force_login(self.auth_user)
        self.account = create_bank_account(self.profile, balance='500')

    def test_debt_payment_create_updates_remaining_amount_and_account_balance(self):
        today = timezone.now().date()
        debt = Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_I_OWE,
            counterparty_name='Chị Linh',
            original_amount=Decimal('200'),
            remaining_amount=Decimal('200'),
            due_date=today + timedelta(days=7),
            status=Debt.STATUS_PENDING,
            is_active=True,
        )

        response = self.client.post(
            reverse('debt_payment_create', args=[debt.debt_id]),
            {
                'bank_account': self.account.bank_account_id,
                'payment_date': today.isoformat(),
                'amount': '120',
                'note': 'Trả một phần',
            },
        )

        self.assertRedirects(response, reverse('debt_detail', args=[debt.debt_id]))

        debt.refresh_from_db()
        self.account.refresh_from_db()

        self.assertEqual(debt.remaining_amount, Decimal('80'))
        self.assertEqual(debt.status, Debt.STATUS_PARTIALLY_PAID)
        self.assertEqual(self.account.current_balance, Decimal('380'))
        self.assertEqual(debt.payments.count(), 1)

    def test_receivable_payment_increases_account_balance_and_uses_collection_copy(self):
        today = timezone.now().date()
        debt = Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_OWED_TO_ME,
            counterparty_name='Anh Minh',
            original_amount=Decimal('200'),
            remaining_amount=Decimal('200'),
            due_date=today + timedelta(days=7),
            status=Debt.STATUS_PENDING,
            is_active=True,
        )

        form_response = self.client.get(reverse('debt_payment_create', args=[debt.debt_id]))
        self.assertContains(form_response, 'Ghi nhận thu nợ')
        self.assertContains(form_response, 'Tài khoản nhận tiền')

        response = self.client.post(
            reverse('debt_payment_create', args=[debt.debt_id]),
            {
                'bank_account': self.account.bank_account_id,
                'payment_date': today.isoformat(),
                'amount': '120',
                'note': 'Đã nhận một phần',
            },
            follow=True,
        )

        debt.refresh_from_db()
        self.account.refresh_from_db()

        self.assertEqual(debt.remaining_amount, Decimal('80'))
        self.assertEqual(debt.status, Debt.STATUS_PARTIALLY_PAID)
        self.assertEqual(self.account.current_balance, Decimal('620'))
        self.assertContains(response, 'Đã thu')
        self.assertContains(response, 'Lịch sử thu nợ')

    def test_debt_list_separates_payable_and_receivable_totals(self):
        today = timezone.now().date()
        Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_I_OWE,
            counterparty_name='Chị Linh',
            original_amount=Decimal('300'),
            remaining_amount=Decimal('80'),
            due_date=today + timedelta(days=3),
            status=Debt.STATUS_PARTIALLY_PAID,
            is_active=True,
        )
        Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_OWED_TO_ME,
            counterparty_name='Anh Minh',
            original_amount=Decimal('200'),
            remaining_amount=Decimal('150'),
            due_date=today + timedelta(days=4),
            status=Debt.STATUS_PARTIALLY_PAID,
            is_active=True,
        )

        response = self.client.get(reverse('debt_list'))

        self.assertEqual(response.context['payable_remaining'], '80 VND')
        self.assertEqual(response.context['receivable_remaining'], '150 VND')
        self.assertEqual(response.context['payable_paid'], '220 VND')
        self.assertEqual(response.context['receivable_collected'], '50 VND')
        self.assertContains(response, 'Ghi nhận trả nợ')
        self.assertContains(response, 'Ghi nhận thu nợ')

    def test_debt_overdue_command_marks_debt_and_creates_alert(self):
        today = timezone.now().date()
        debt = Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_I_OWE,
            counterparty_name='Anh Nam',
            original_amount=Decimal('300'),
            remaining_amount=Decimal('120'),
            due_date=today - timedelta(days=1),
            status=Debt.STATUS_PENDING,
            is_active=True,
        )

        stdout = StringIO()
        call_command('debt_overdue_check', date=today.isoformat(), stdout=stdout)

        debt.refresh_from_db()
        self.assertEqual(debt.status, Debt.STATUS_OVERDUE)
        self.assertTrue(
            Alert.objects.filter(
                user=self.profile,
                alert_type=Alert.TYPE_DEBT_OVERDUE,
                related_debt_id=debt.debt_id,
            ).exists()
        )
        self.assertIn('checked=1, created=1', stdout.getvalue())

    def test_debt_detail_returns_404_for_other_users_debt(self):
        today = timezone.now().date()
        _, other_profile = create_user_pair(username='other', email='other@example.com')
        other_debt = Debt.objects.create(
            user=other_profile,
            debt_type=Debt.TYPE_I_OWE,
            counterparty_name='Người khác',
            original_amount=Decimal('180'),
            remaining_amount=Decimal('180'),
            due_date=today + timedelta(days=3),
            status=Debt.STATUS_PENDING,
            is_active=True,
        )

        response = self.client.get(reverse('debt_detail', args=[other_debt.debt_id]))

        self.assertEqual(response.status_code, 404)
