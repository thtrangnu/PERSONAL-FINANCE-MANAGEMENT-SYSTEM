from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date

from apps.debts.models import Debt
from apps.debts.services import sync_debt_status_and_alert


class Command(BaseCommand):
    help = 'Kiểm tra các khoản nợ quá hạn và tạo cảnh báo nếu cần.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            help='Ngày kiểm tra theo định dạng YYYY-MM-DD. Mặc định là hôm nay.',
        )

    def handle(self, *args, **options):
        target_date = parse_date(options['date']) if options.get('date') else date.today()
        if target_date is None:
            raise CommandError('Ngày không hợp lệ. Hãy dùng định dạng YYYY-MM-DD.')

        checked = 0
        created = 0

        debts = (
            Debt.objects.select_related('user')
            .filter(
                is_active=True,
                remaining_amount__gt=0,
                due_date__lt=target_date,
            )
            .order_by('user_id', 'due_date', 'debt_id')
        )

        for debt in debts:
            checked += 1
            _, is_created = sync_debt_status_and_alert(debt)
            if is_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Debt overdue check done for {target_date:%Y-%m-%d}: '
                f'checked={checked}, created={created}'
            )
        )
