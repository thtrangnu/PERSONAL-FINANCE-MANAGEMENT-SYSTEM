from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import connection

from apps.accounts.models import UserProfile
from apps.bank_accounts.models import BankAccount
from apps.budgets.models import Budget
from apps.categories.models import ExpenseCategory

_APPLIED_SQL_FILES = set()


def create_user_pair(
    username='alice',
    email=None,
    password='testpass123',
    *,
    currency='VND',
):
    email = email or f'{username}@example.com'
    auth_user = get_user_model().objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    profile = UserProfile.objects.create(
        username=username,
        email=email,
        password_hash=auth_user.password,
        full_name=username.title(),
        default_currency=currency,
    )
    return auth_user, profile


def create_category(profile, name='Ăn uống', *, category_type=ExpenseCategory.TYPE_EXPENSE):
    return ExpenseCategory.objects.create(
        user=profile,
        category_name=name,
        category_type=category_type,
        is_default=False,
        is_active=True,
    )


def create_bank_account(profile, name='Ví tiền mặt', *, balance='0', account_type=BankAccount.TYPE_CASH):
    amount = Decimal(balance)
    return BankAccount.objects.create(
        user=profile,
        account_name=name,
        account_type=account_type,
        currency=profile.default_currency or 'VND',
        opening_balance=amount,
        current_balance=amount,
        is_active=True,
    )


def create_budget(
    profile,
    *,
    name='Ngân sách tháng',
    scope=Budget.SCOPE_OVERALL,
    category=None,
    month=1,
    year=2026,
    spending_limit='100',
    warning_percent='80',
    status=Budget.STATUS_ACTIVE,
):
    return Budget.objects.create(
        user=profile,
        budget_name=name,
        budget_scope=scope,
        category=category,
        period_month=month,
        period_year=year,
        spending_limit=Decimal(spending_limit),
        warning_percent=Decimal(warning_percent),
        status=status,
    )


def _iter_mysql_statements(sql_text):
    delimiter = ';'
    buffer = []

    for raw_line in sql_text.splitlines():
        stripped = raw_line.strip()
        upper = stripped.upper()

        if not stripped or stripped.startswith('--'):
            continue
        if upper.startswith('DELIMITER '):
            delimiter = stripped.split(None, 1)[1]
            continue
        if upper.startswith('USE '):
            continue
        if upper.startswith('SET NAMES '):
            continue

        buffer.append(raw_line)
        candidate = '\n'.join(buffer).rstrip()
        if candidate.endswith(delimiter):
            statement = candidate[: -len(delimiter)].strip()
            if statement:
                yield statement
            buffer = []

    tail = '\n'.join(buffer).strip()
    if tail:
        yield tail


def install_mysql_sql_files(*relative_paths):
    if connection.vendor != 'mysql':
        return

    repo_root = Path(__file__).resolve().parents[2]
    applied_triggers = False

    with connection.cursor() as cursor:
        for relative_path in relative_paths:
            abs_path = repo_root / relative_path
            cache_key = (connection.settings_dict.get('NAME'), str(abs_path))
            if cache_key in _APPLIED_SQL_FILES:
                continue

            sql_text = abs_path.read_text(encoding='utf-8')
            for statement in _iter_mysql_statements(sql_text):
                cursor.execute(statement)

            _APPLIED_SQL_FILES.add(cache_key)
            applied_triggers = applied_triggers or abs_path.name == 'triggers.sql'

    if applied_triggers:
        from apps.bank_accounts.balance import database_trigger_exists

        database_trigger_exists.cache_clear()
