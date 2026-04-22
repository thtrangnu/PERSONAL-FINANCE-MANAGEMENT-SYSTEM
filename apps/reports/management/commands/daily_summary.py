import csv
import json
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Sum
from django.utils.dateparse import parse_date

from apps.accounts.models import UserProfile
from apps.expenses.models import Expense
from apps.income.models import Income


def money(value):
    return str(value.quantize(Decimal('0.01')))


class Command(BaseCommand):
    help = 'Tổng hợp thu nhập và chi tiêu theo ngày để chạy bằng Cloud Run Job.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            help='Ngày cần tổng hợp, định dạng YYYY-MM-DD. Mặc định là hôm nay.',
        )

    def handle(self, *args, **options):
        target_date = parse_date(options['date']) if options.get('date') else date.today()
        if target_date is None:
            raise CommandError('Ngày không hợp lệ. Hãy dùng định dạng YYYY-MM-DD.')

        income_map = {
            row['user_id']: row
            for row in Income.objects.filter(
                income_date=target_date,
                status=Income.STATUS_ACTIVE,
            )
            .values('user_id')
            .annotate(total=Sum('amount'), count=Count('income_id'))
        }
        expense_map = {
            row['user_id']: row
            for row in Expense.objects.filter(
                expense_date=target_date,
                status=Expense.STATUS_ACTIVE,
            )
            .values('user_id')
            .annotate(total=Sum('amount'), count=Count('expense_id'))
        }

        rows = []
        total_income = Decimal('0.00')
        total_expense = Decimal('0.00')

        for user in UserProfile.objects.filter(is_active=True).order_by('username'):
            income_total = income_map.get(user.user_id, {}).get('total') or Decimal('0.00')
            expense_total = expense_map.get(user.user_id, {}).get('total') or Decimal('0.00')
            income_count = income_map.get(user.user_id, {}).get('count', 0)
            expense_count = expense_map.get(user.user_id, {}).get('count', 0)
            net_total = income_total - expense_total

            total_income += income_total
            total_expense += expense_total
            rows.append(
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'income_count': income_count,
                    'income_total': money(income_total),
                    'expense_count': expense_count,
                    'expense_total': money(expense_total),
                    'net_total': money(net_total),
                }
            )

        output_dir = settings.REPORT_OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = f'daily_summary_{target_date:%Y-%m-%d}'
        json_path = output_dir / f'{base_name}.json'
        csv_path = output_dir / f'{base_name}.csv'

        payload = {
            'date': target_date.isoformat(),
            'totals': {
                'income': money(total_income),
                'expense': money(total_expense),
                'net': money(total_income - total_expense),
            },
            'users': rows,
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

        with csv_path.open('w', newline='', encoding='utf-8-sig') as file:
            fieldnames = [
                'user_id',
                'username',
                'email',
                'income_count',
                'income_total',
                'expense_count',
                'expense_total',
                'net_total',
            ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.stdout.write(
            self.style.SUCCESS(
                f'Daily summary ready: {json_path} | {csv_path} '
                f'(income={money(total_income)}, expense={money(total_expense)})'
            )
        )
