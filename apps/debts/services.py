from decimal import Decimal

from django.utils import timezone

from apps.alerts.models import Alert
from apps.debts.models import Debt


def _format_money(amount, currency='VND'):
    amount = amount or 0
    if currency == 'VND':
        return f'{amount:,.0f} {currency}'.replace(',', '.')
    return f'{amount:,.2f} {currency}'


def refresh_debt_status(debt, save=True):
    today = timezone.now().date()
    update_fields = {'updated_at'}

    if debt.remaining_amount <= 0:
        normalized_remaining = Decimal('0')
        if debt.remaining_amount != normalized_remaining:
            debt.remaining_amount = normalized_remaining
            update_fields.add('remaining_amount')
        next_status = Debt.STATUS_PAID
        next_active = False
    elif debt.due_date and debt.due_date < today:
        next_status = Debt.STATUS_OVERDUE
        next_active = True
    elif debt.remaining_amount < debt.original_amount:
        next_status = Debt.STATUS_PARTIALLY_PAID
        next_active = True
    else:
        next_status = Debt.STATUS_PENDING
        next_active = True

    if debt.status != next_status:
        debt.status = next_status
        update_fields.add('status')
    if debt.is_active != next_active:
        debt.is_active = next_active
        update_fields.add('is_active')

    if save and len(update_fields) > 1:
        debt.save(update_fields=list(update_fields))

    return debt


def ensure_overdue_alert(debt):
    if debt.status != Debt.STATUS_OVERDUE or debt.remaining_amount <= 0:
        return None, False

    existing = Alert.objects.filter(
        user=debt.user,
        alert_type=Alert.TYPE_DEBT_OVERDUE,
        related_debt_id=debt.debt_id,
    ).exists()
    if existing:
        return None, False

    currency = debt.user.default_currency or 'VND'
    due_label = debt.due_date.strftime('%d/%m/%Y') if debt.due_date else 'không có hạn'
    alert = Alert.objects.create(
        user=debt.user,
        alert_type=Alert.TYPE_DEBT_OVERDUE,
        severity=Alert.SEVERITY_CRITICAL,
        title=f'Khoản nợ với {debt.counterparty_name} đã quá hạn',
        message=(
            f'Khoản nợ "{debt.counterparty_name}" đã quá hạn từ {due_label}. '
            f'Số tiền còn lại là {_format_money(debt.remaining_amount, currency)}.'
        ),
        related_debt_id=debt.debt_id,
    )
    return alert, True


def sync_debt_status_and_alert(debt, save=True):
    refresh_debt_status(debt, save=save)
    return ensure_overdue_alert(debt)
