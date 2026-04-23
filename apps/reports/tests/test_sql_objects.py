from decimal import Decimal

from django.db import DatabaseError, connection
from django.test import TransactionTestCase
from django.utils import timezone

from apps.alerts.models import Alert
from apps.expenses.models import Expense
from apps.income.models import Income
from apps.tests.support import (
    create_bank_account,
    create_budget,
    create_category,
    create_user_pair,
    install_mysql_sql_files,
)


class SqlObjectIntegrationTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        install_mysql_sql_files(
            'sql/functions.sql',
            'sql/views.sql',
            'sql/procedures.sql',
            'sql/triggers.sql',
        )

    def setUp(self):
        self.auth_user, self.profile = create_user_pair(username='sql-user', email='sql@example.com')
        self.expense_category = create_category(self.profile, name='Ăn uống')
        self.income_category = create_category(
            self.profile,
            name='Lương',
            category_type='income',
        )
        self.account = create_bank_account(self.profile, balance='500')

    def test_sql_function_and_view_return_expected_budget_metrics(self):
        today = timezone.now().date()
        budget = create_budget(
            self.profile,
            scope='category',
            category=self.expense_category,
            month=today.month,
            year=today.year,
            spending_limit='100',
            warning_percent='80',
        )
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
            amount=Decimal('85'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT fn_monthly_net_amount(%s, %s, %s)',
                [self.profile.user_id, today.year, today.month],
            )
            net_amount = cursor.fetchone()[0]
            cursor.execute(
                '''
                SELECT amount_used, remaining_amount, usage_percent, usage_status
                FROM vw_budget_usage
                WHERE budget_id = %s
                ''',
                [budget.budget_id],
            )
            amount_used, remaining_amount, usage_percent, usage_status = cursor.fetchone()

        self.assertEqual(net_amount, Decimal('915.00'))
        self.assertEqual(amount_used, Decimal('85.00'))
        self.assertEqual(remaining_amount, Decimal('15.00'))
        self.assertEqual(usage_percent, Decimal('85.00'))
        self.assertEqual(usage_status, 'warning')

    def test_stored_procedure_monthly_summary_returns_expected_totals(self):
        today = timezone.now().date()
        Income.objects.create(
            user=self.profile,
            category=self.income_category,
            bank_account=self.account,
            title='Lương tháng',
            amount=Decimal('1200'),
            income_date=today,
            status=Income.STATUS_ACTIVE,
        )
        Expense.objects.create(
            user=self.profile,
            category=self.expense_category,
            bank_account=self.account,
            amount=Decimal('450'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )
        Alert.objects.create(
            user=self.profile,
            alert_type=Alert.TYPE_OTHER,
            severity=Alert.SEVERITY_INFO,
            title='Thông tin',
            message='Alert test',
        )

        with connection.cursor() as cursor:
            cursor.execute(
                'CALL sp_monthly_summary(%s, %s, %s)',
                [self.profile.user_id, today.year, today.month],
            )
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            while cursor.nextset():
                pass

        summary = dict(zip(columns, row))
        self.assertEqual(summary['total_income'], Decimal('1200.00'))
        self.assertEqual(summary['total_expense'], Decimal('450.00'))
        self.assertEqual(summary['net_amount'], Decimal('750.00'))
        self.assertEqual(summary['unread_alert_count'], 1)
        self.assertEqual(summary['total_active_balance'], Decimal('1250.00'))

    def test_alert_trigger_rejects_multiple_related_objects(self):
        today = timezone.now().date()
        budget = create_budget(
            self.profile,
            month=today.month,
            year=today.year,
            spending_limit='300',
        )
        expense = Expense.objects.create(
            user=self.profile,
            category=self.expense_category,
            bank_account=self.account,
            amount=Decimal('40'),
            expense_date=today,
            status=Expense.STATUS_ACTIVE,
        )

        with self.assertRaises(DatabaseError):
            Alert.objects.create(
                user=self.profile,
                alert_type=Alert.TYPE_BUDGET_WARNING,
                severity=Alert.SEVERITY_WARNING,
                title='Alert lỗi',
                message='Không hợp lệ',
                related_budget=budget,
                related_expense=expense,
            )
