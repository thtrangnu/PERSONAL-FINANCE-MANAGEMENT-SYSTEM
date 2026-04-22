import calendar
from datetime import date, datetime, time
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from apps.alerts.models import Alert
from apps.budgets.models import Budget
from apps.expenses.models import Expense


def month_bounds(year, month):
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def money(value):
    return f'{value.quantize(Decimal("0.01"))}'


class Command(BaseCommand):
    help = 'Kiểm tra ngân sách và tạo cảnh báo, phù hợp chạy định kỳ bằng Cloud Run Job.'

    def add_arguments(self, parser):
        today = date.today()
        parser.add_argument('--year', type=int, default=today.year)
        parser.add_argument('--month', type=int, default=today.month)

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        if month < 1 or month > 12:
            raise CommandError('Tháng không hợp lệ. Giá trị hợp lệ là 1 đến 12.')

        start_date, end_date = month_bounds(year, month)
        alert_window_start = datetime.combine(start_date, time.min)
        alert_window_end = datetime.combine(end_date, time.max)
        checked = 0
        created = 0
        skipped = 0

        budgets = (
            Budget.objects.select_related('user', 'category')
            .filter(
                status=Budget.STATUS_ACTIVE,
                period_year=year,
                period_month=month,
            )
            .order_by('user_id', 'budget_name')
        )

        for budget in budgets:
            checked += 1
            expenses = Expense.objects.filter(
                user=budget.user,
                expense_date__gte=start_date,
                expense_date__lte=end_date,
                status=Expense.STATUS_ACTIVE,
            )
            if budget.budget_scope == Budget.SCOPE_CATEGORY and budget.category_id:
                expenses = expenses.filter(category=budget.category)

            spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            if spent <= 0:
                skipped += 1
                continue

            percent = (spent / budget.spending_limit) * Decimal('100')
            if spent >= budget.spending_limit:
                alert_type = Alert.TYPE_BUDGET_EXCEEDED
                severity = Alert.SEVERITY_CRITICAL
                title = f'Ngân sách {budget.budget_name} đã vượt giới hạn'
                message = (
                    f'Bạn đã chi {money(spent)} trên giới hạn {money(budget.spending_limit)} '
                    f'trong tháng {month}/{year}.'
                )
            elif percent >= budget.warning_percent:
                alert_type = Alert.TYPE_BUDGET_WARNING
                severity = Alert.SEVERITY_WARNING
                title = f'Ngân sách {budget.budget_name} sắp chạm giới hạn'
                message = (
                    f'Bạn đã dùng {percent.quantize(Decimal("0.01"))}% ngân sách '
                    f'({money(spent)} / {money(budget.spending_limit)}) trong tháng {month}/{year}.'
                )
            else:
                skipped += 1
                continue

            exists = Alert.objects.filter(
                user=budget.user,
                related_budget=budget,
                alert_type=alert_type,
                created_at__gte=alert_window_start,
                created_at__lte=alert_window_end,
            ).exists()
            if exists:
                skipped += 1
                continue

            Alert.objects.create(
                user=budget.user,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                related_budget=budget,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Budget alert check done for {month}/{year}: '
                f'checked={checked}, created={created}, skipped={skipped}'
            )
        )
