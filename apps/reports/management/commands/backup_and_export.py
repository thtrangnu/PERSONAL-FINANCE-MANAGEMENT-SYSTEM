import csv
import json
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


TABLES_TO_EXPORT = [
    'auth_user',
    'users',
    'categories',
    'bank_accounts',
    'incomes',
    'expenses',
    'budgets',
    'alerts',
    'debts',
    'debt_payments',
    'groups',
    'group_members',
    'shared_transactions',
]


def serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return value


class Command(BaseCommand):
    help = 'Xuất dữ liệu quan trọng ra CSV/manifest để dùng cho backup hoặc Cloud Run Job.'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = settings.REPORT_OUTPUT_DIR / f'backup_{timestamp}'
        output_dir.mkdir(parents=True, exist_ok=True)

        existing_tables = set(connection.introspection.table_names())
        manifest = {
            'created_at': datetime.now().isoformat(timespec='seconds'),
            'database': str(connection.settings_dict.get('NAME')),
            'files': [],
            'missing_tables': [],
            'cloud_storage_bucket': settings.GS_BUCKET_NAME or '',
        }

        with connection.cursor() as cursor:
            for table_name in TABLES_TO_EXPORT:
                if table_name not in existing_tables:
                    manifest['missing_tables'].append(table_name)
                    continue

                quoted_table = connection.ops.quote_name(table_name)
                cursor.execute(f'SELECT * FROM {quoted_table}')
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                csv_path = output_dir / f'{table_name}.csv'

                with csv_path.open('w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(columns)
                    writer.writerows([[serialize(value) for value in row] for row in rows])

                manifest['files'].append(
                    {
                        'table': table_name,
                        'file': csv_path.name,
                        'rows': len(rows),
                    }
                )

        manifest_path = output_dir / 'manifest.json'
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

        bucket_note = ''
        if settings.GS_BUCKET_NAME:
            bucket_note = f' | Cloud Storage target: gs://{settings.GS_BUCKET_NAME}/backups/'

        self.stdout.write(
            self.style.SUCCESS(
                f'Backup/export ready: {output_dir} '
                f'({len(manifest["files"])} files){bucket_note}'
            )
        )
