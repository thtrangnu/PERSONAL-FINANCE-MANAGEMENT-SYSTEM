from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.budgets.models import Budget
from apps.expenses.models import Expense
from apps.tests.support import create_bank_account, create_category, create_user_pair


class BudgetViewTests(TestCase):
    def setUp(self):
        self.auth_user, self.profile = create_user_pair()
        self.client.force_login(self.auth_user)
        self.category = create_category(self.profile, name='Ăn uống')
        self.account = create_bank_account(self.profile, balance='1000')

    def test_budget_create_overall_scope_clears_posted_category(self):
        today = timezone.now().date()

        response = self.client.post(
            reverse('budget_create'),
            {
                'budget_name': 'Ngân sách tháng',
                'budget_scope': Budget.SCOPE_OVERALL,
                'category': self.category.category_id,
                'period_month': today.month,
                'period_year': today.year,
                'spending_limit': '500',
                'warning_percent': '80',
                'status': Budget.STATUS_ACTIVE,
            },
        )

        self.assertRedirects(response, reverse('budget_list'))

        budget = Budget.objects.get(user=self.profile)
        self.assertEqual(budget.budget_scope, Budget.SCOPE_OVERALL)
        self.assertIsNone(budget.category)

    def test_budget_list_attaches_usage_metrics_from_expenses(self):
        today = timezone.now().date()
        budget = Budget.objects.create(
            user=self.profile,
            budget_name='Ngân sách ăn uống',
            budget_scope=Budget.SCOPE_CATEGORY,
            category=self.category,
            period_month=today.month,
            period_year=today.year,
            spending_limit=Decimal('200'),
            warning_percent=Decimal('80'),
            status=Budget.STATUS_ACTIVE,
        )
        Expense.objects.create(
            user=self.profile,
            category=self.category,
            bank_account=self.account,
            amount=Decimal('50'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )
        Expense.objects.create(
            user=self.profile,
            category=self.category,
            bank_account=self.account,
            amount=Decimal('30'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )

        response = self.client.get(reverse('budget_list'))

        rendered_budget = response.context['budgets'][0]
        self.assertEqual(rendered_budget.budget_id, budget.budget_id)
        self.assertEqual(rendered_budget.usage_percent, 40)
        self.assertEqual(rendered_budget.used_amount, '80 VND')
        self.assertEqual(rendered_budget.remaining_amount, '120 VND')

    def test_budget_update_returns_404_for_other_users_budget(self):
        today = timezone.now().date()
        _, other_profile = create_user_pair(username='other', email='other@example.com')
        other_category = create_category(other_profile, name='Di chuyển')
        other_budget = Budget.objects.create(
            user=other_profile,
            budget_name='Ngân sách khác',
            budget_scope=Budget.SCOPE_CATEGORY,
            category=other_category,
            period_month=today.month,
            period_year=today.year,
            spending_limit=Decimal('300'),
            warning_percent=Decimal('75'),
            status=Budget.STATUS_ACTIVE,
        )

        response = self.client.get(reverse('budget_update', args=[other_budget.budget_id]))

        self.assertEqual(response.status_code, 404)
