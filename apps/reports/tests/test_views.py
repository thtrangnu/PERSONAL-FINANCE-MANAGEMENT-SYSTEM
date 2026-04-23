from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.expenses.models import Expense
from apps.income.models import Income
from apps.tests.support import create_bank_account, create_budget, create_category, create_user_pair


class ReportViewTests(TestCase):
    def setUp(self):
        self.auth_user, self.profile = create_user_pair()
        self.client.force_login(self.auth_user)
        self.expense_category = create_category(self.profile, name='Ăn uống')
        self.income_category = create_category(
            self.profile,
            name='Lương',
            category_type='income',
        )
        self.account = create_bank_account(self.profile, balance='700')

    def test_monthly_summary_aggregates_financial_totals(self):
        today = timezone.now().date()
        Income.objects.create(
            user=self.profile,
            category=self.income_category,
            bank_account=self.account,
            title='Lương tháng',
            amount=Decimal('1000'),
            income_date=today,
            status=Income.STATUS_ACTIVE,
        )
        Expense.objects.create(
            user=self.profile,
            category=self.expense_category,
            bank_account=self.account,
            amount=Decimal('300'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )
        create_budget(
            self.profile,
            month=today.month,
            year=today.year,
            spending_limit='500',
        )

        response = self.client.get(
            reverse('report_monthly'),
            {'year': today.year, 'month': today.month},
        )

        summary = {row['label']: row['value'] for row in response.context['summary_rows']}
        self.assertEqual(summary['Tổng tiền vào'], '1.000 VND')
        self.assertEqual(summary['Tổng tiền ra'], '300 VND')
        self.assertEqual(summary['Chênh lệch'], '700 VND')
        self.assertEqual(summary['Ngân sách đã đặt'], '500 VND')
        self.assertEqual(summary['Số tiền hiện có'], '700 VND')

    def test_overview_summary_respects_selected_date_range(self):
        today = timezone.now().date()
        in_range_day = today - timedelta(days=2)
        out_of_range_day = today - timedelta(days=25)

        Income.objects.create(
            user=self.profile,
            category=self.income_category,
            bank_account=self.account,
            title='Freelance',
            amount=Decimal('400'),
            income_date=in_range_day,
            status=Income.STATUS_ACTIVE,
        )
        Income.objects.create(
            user=self.profile,
            category=self.income_category,
            bank_account=self.account,
            title='Lương cũ',
            amount=Decimal('900'),
            income_date=out_of_range_day,
            status=Income.STATUS_ACTIVE,
        )
        Expense.objects.create(
            user=self.profile,
            category=self.expense_category,
            bank_account=self.account,
            amount=Decimal('100'),
            expense_date=in_range_day,
            status=Expense.STATUS_ACTIVE,
        )

        response = self.client.get(
            reverse('report_overview'),
            {
                'start_date': (today - timedelta(days=7)).isoformat(),
                'end_date': today.isoformat(),
            },
        )

        summary = {row['label']: row['value'] for row in response.context['summary_rows']}
        self.assertEqual(summary['Tổng tiền vào'], '400 VND')
        self.assertEqual(summary['Tổng tiền ra'], '100 VND')
        self.assertEqual(summary['Chênh lệch'], '300 VND')
