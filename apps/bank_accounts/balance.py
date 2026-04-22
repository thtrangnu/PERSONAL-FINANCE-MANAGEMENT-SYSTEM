from functools import lru_cache

from django.db import DatabaseError, connection
from django.db.models import F

from apps.bank_accounts.models import BankAccount


@lru_cache(maxsize=None)
def database_trigger_exists(trigger_name):
    if connection.vendor != 'mysql':
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.TRIGGERS
                WHERE TRIGGER_SCHEMA = DATABASE()
                  AND TRIGGER_NAME = %s
                """,
                [trigger_name],
            )
            row = cursor.fetchone()
    except DatabaseError:
        return False

    return bool(row and row[0])


def database_handles_balance(*trigger_names):
    return any(database_trigger_exists(trigger_name) for trigger_name in trigger_names)


def adjust_balance(account_id, amount_delta, trigger_names=()):
    if account_id is None:
        return
    if trigger_names and database_handles_balance(*trigger_names):
        return

    BankAccount.objects.filter(bank_account_id=account_id).update(
        current_balance=F('current_balance') + amount_delta,
    )
