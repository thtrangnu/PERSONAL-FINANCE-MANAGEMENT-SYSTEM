from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.debts.models import Debt
from apps.tests.support import create_bank_account, create_user_pair


class BankAccountDetailTests(TestCase):
    def setUp(self):
        self.auth_user, self.profile = create_user_pair()
        self.client.force_login(self.auth_user)
        self.account = create_bank_account(self.profile, balance='500')

    def test_debt_payments_are_shown_as_account_cashflow(self):
        today = timezone.now().date()
        payable = Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_I_OWE,
            counterparty_name='Chị Linh',
            original_amount=Decimal('100'),
            remaining_amount=Decimal('100'),
            due_date=today + timedelta(days=5),
            status=Debt.STATUS_PENDING,
            is_active=True,
        )
        receivable = Debt.objects.create(
            user=self.profile,
            debt_type=Debt.TYPE_OWED_TO_ME,
            counterparty_name='Anh Minh',
            original_amount=Decimal('120'),
            remaining_amount=Decimal('120'),
            due_date=today + timedelta(days=5),
            status=Debt.STATUS_PENDING,
            is_active=True,
        )

        self.client.post(
            reverse('debt_payment_create', args=[payable.debt_id]),
            {
                'bank_account': self.account.bank_account_id,
                'payment_date': today.isoformat(),
                'amount': '40',
                'note': 'Trả bớt',
            },
        )
        self.client.post(
            reverse('debt_payment_create', args=[receivable.debt_id]),
            {
                'bank_account': self.account.bank_account_id,
                'payment_date': today.isoformat(),
                'amount': '70',
                'note': 'Đã nhận',
            },
        )

        self.account.refresh_from_db()
        response = self.client.get(reverse('bank_account_detail', args=[self.account.bank_account_id]))

        self.assertEqual(self.account.current_balance, Decimal('530'))
        self.assertContains(response, 'Thu nợ từ Anh Minh')
        self.assertContains(response, 'Trả nợ cho Chị Linh')
        self.assertContains(response, 'Tổng tiền vào')
        self.assertContains(response, '70 VND')
        self.assertContains(response, 'Tổng tiền ra')
        self.assertContains(response, '40 VND')
