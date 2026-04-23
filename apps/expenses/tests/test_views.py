from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.alerts.models import Alert
from apps.budgets.models import Budget
from apps.expenses.models import Expense
from apps.tests.support import create_bank_account, create_budget, create_category, create_user_pair


class ExpenseFlowTests(TestCase):
    def setUp(self):
        self.auth_user, self.profile = create_user_pair()
        self.client.force_login(self.auth_user)
        self.category = create_category(self.profile, name='Ăn uống')
        self.account = create_bank_account(self.profile, balance='1000')

    def test_expense_create_updates_balance_and_creates_budget_alert(self):
        today = timezone.now().date()
        budget = create_budget(
            self.profile,
            scope=Budget.SCOPE_CATEGORY,
            category=self.category,
            month=today.month,
            year=today.year,
            spending_limit='100',
            warning_percent='80',
        )

        response = self.client.post(
            reverse('expense_create'),
            {
                'category': self.category.category_id,
                'bank_account': self.account.bank_account_id,
                'amount': '85',
                'expense_date': today.isoformat(),
                'payment_method': Expense.METHOD_CASH,
                'description': 'Ăn trưa',
            },
        )

        self.assertRedirects(response, reverse('expense_list'))

        expense = Expense.objects.get(user=self.profile)
        self.account.refresh_from_db()

        self.assertEqual(expense.amount, Decimal('85'))
        self.assertEqual(self.account.current_balance, Decimal('915'))

        alert = Alert.objects.get(user=self.profile, related_budget=budget, related_expense=expense)
        self.assertEqual(alert.alert_type, Alert.TYPE_BUDGET_WARNING)
        self.assertEqual(alert.severity, Alert.SEVERITY_WARNING)

    def test_expense_list_only_shows_current_users_expenses(self):
        today = timezone.now().date()
        own_expense = Expense.objects.create(
            user=self.profile,
            category=self.category,
            bank_account=self.account,
            amount=Decimal('50'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )

        _, other_profile = create_user_pair(username='other', email='other@example.com')
        other_category = create_category(other_profile, name='Di chuyển')
        other_account = create_bank_account(other_profile, name='Ví khác', balance='500')
        other_expense = Expense.objects.create(
            user=other_profile,
            category=other_category,
            bank_account=other_account,
            amount=Decimal('90'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )

        response = self.client.get(reverse('expense_list'))

        visible_ids = {expense.expense_id for expense in response.context['expenses']}
        self.assertIn(own_expense.expense_id, visible_ids)
        self.assertNotIn(other_expense.expense_id, visible_ids)

    def test_expense_update_returns_404_for_other_users_expense(self):
        today = timezone.now().date()
        _, other_profile = create_user_pair(username='other', email='other@example.com')
        other_category = create_category(other_profile, name='Di chuyển')
        other_account = create_bank_account(other_profile, name='Ví khác', balance='500')
        other_expense = Expense.objects.create(
            user=other_profile,
            category=other_category,
            bank_account=other_account,
            amount=Decimal('90'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )

        response = self.client.get(reverse('expense_update', args=[other_expense.expense_id]))

        self.assertEqual(response.status_code, 404)
