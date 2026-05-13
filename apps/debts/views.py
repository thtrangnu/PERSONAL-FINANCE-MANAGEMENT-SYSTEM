from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection, transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.bank_accounts.balance import database_trigger_exists
from apps.bank_accounts.models import BankAccount
from apps.debts.forms import DebtForm, DebtPaymentForm
from apps.debts.models import Debt
from apps.debts.services import sync_debt_status_and_alert


def _get_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        username=user.username,
        defaults={
            'email': user.email,
            'password_hash': user.password,
            'full_name': user.get_full_name() or user.username,
            'role': UserProfile.ROLE_ADMIN if user.is_staff else UserProfile.ROLE_USER,
            'is_active': user.is_active,
        },
    )
    return profile


def _format_money(amount, currency='VND'):
    amount = amount or 0
    if currency == 'VND':
        return f'{amount:,.0f} {currency}'.replace(',', '.')
    return f'{amount:,.2f} {currency}'


def _sum_amount(queryset, field_name):
    return queryset.aggregate(total=Sum(field_name))['total'] or Decimal('0')


def _can_add_payment(debt):
    return debt.is_active and debt.status != Debt.STATUS_PAID and debt.remaining_amount > 0


def _debt_labels(debt):
    if debt.debt_type == Debt.TYPE_OWED_TO_ME:
        return {
            'action_label': 'Ghi nhận thu nợ',
            'detail_copy': 'Theo dõi lịch sử thu tiền và số còn phải thu của khoản này.',
            'empty_payment_help': 'Ghi nhận lần thu đầu tiên để cập nhật số còn phải thu.',
            'empty_payment_title': 'Chưa có lần thu',
            'history_title': 'Lịch sử thu nợ',
            'page_title': 'Ghi nhận thu nợ',
            'payment_eyebrow': 'Thu nợ',
            'payment_intro': f'Ghi nhận số tiền đã nhận từ {debt.counterparty_name} vào một tài khoản trong NUFI.',
            'payment_mode_copy': 'Chọn thu toàn bộ để tự điền số còn phải thu, hoặc thu một phần để nhập số tiền nhỏ hơn. Tài khoản nhận tiền là bắt buộc để hệ thống cộng số dư.',
            'payment_mode_label': 'Cách thu nợ',
            'payoff_button_label': 'Thu toàn bộ',
            'payoff_copy': 'Bạn đang ghi nhận thu toàn bộ. Số tiền sẽ được điền đúng bằng {amount}.',
            'payoff_submit_label': 'Lưu thu toàn bộ',
            'partial_button_label': 'Thu một phần',
            'partial_copy': 'Bạn đang ghi nhận thu một phần. Hãy nhập số tiền nhỏ hơn khoản còn phải thu và chọn tài khoản nhận tiền trong NUFI.',
            'progress_help': 'Các lần thu tiền đã ghi nhận.',
            'progress_label': 'Đã thu',
            'remaining_help': 'Đây là mức tối đa có thể ghi nhận thu.',
            'remaining_label': 'Còn phải thu',
            'submit_label': 'Lưu lần thu',
            'success_full': 'Đã ghi nhận thu toàn bộ khoản phải thu.',
            'success_partial': 'Đã ghi nhận thu nợ một phần.',
            'warning_text': 'Số tiền đang lớn hơn khoản còn phải thu. Vui lòng giảm xuống không quá {amount}.',
        }

    return {
        'action_label': 'Ghi nhận trả nợ',
        'detail_copy': 'Theo dõi lịch sử trả tiền và số còn phải trả của khoản nợ này.',
        'empty_payment_help': 'Ghi nhận lần trả đầu tiên để cập nhật số còn phải trả.',
        'empty_payment_title': 'Chưa có lần trả',
        'history_title': 'Lịch sử trả nợ',
        'page_title': 'Ghi nhận trả nợ',
        'payment_eyebrow': 'Trả nợ',
        'payment_intro': f'Ghi nhận số tiền đã trả cho {debt.counterparty_name} bằng một tài khoản trong NUFI.',
        'payment_mode_copy': 'Chọn trả toàn bộ để tự điền số còn phải trả, hoặc trả một phần để nhập số tiền nhỏ hơn. Tài khoản thanh toán là bắt buộc để hệ thống trừ số dư.',
        'payment_mode_label': 'Cách trả nợ',
        'payoff_button_label': 'Trả toàn bộ',
        'payoff_copy': 'Bạn đang ghi nhận trả toàn bộ. Số tiền sẽ được điền đúng bằng {amount}.',
        'payoff_submit_label': 'Lưu trả toàn bộ',
        'partial_button_label': 'Trả một phần',
        'partial_copy': 'Bạn đang ghi nhận trả một phần. Hãy nhập số tiền nhỏ hơn khoản còn phải trả và chọn tài khoản thanh toán trong NUFI.',
        'progress_help': 'Các lần trả tiền đã ghi nhận.',
        'progress_label': 'Đã trả',
        'remaining_help': 'Đây là mức tối đa có thể ghi nhận trả.',
        'remaining_label': 'Còn phải trả',
        'submit_label': 'Lưu lần trả',
        'success_full': 'Đã ghi nhận trả toàn bộ khoản nợ.',
        'success_partial': 'Đã ghi nhận trả nợ một phần.',
        'warning_text': 'Số tiền đang lớn hơn khoản còn phải trả. Vui lòng giảm xuống không quá {amount}.',
    }


def _database_handles_debt_updates():
    if connection.vendor != 'mysql':
        return False
    return database_trigger_exists('trg_debt_payments_ai_update_debt')


@login_required
def debt_list(request):
    profile = _get_profile(request.user)
    debts = list(Debt.objects.filter(user=profile).order_by('-is_active', 'due_date', '-debt_id'))
    currency = profile.default_currency or 'VND'

    for debt in debts:
        sync_debt_status_and_alert(debt)
        labels = _debt_labels(debt)
        debt.formatted_original = _format_money(debt.original_amount, currency)
        debt.formatted_remaining = _format_money(debt.remaining_amount, currency)
        debt.can_add_payment = _can_add_payment(debt)
        debt.action_label = labels['action_label']
        debt.remaining_label = labels['remaining_label']

    base_qs = Debt.objects.filter(user=profile)
    payable_qs = base_qs.filter(debt_type=Debt.TYPE_I_OWE)
    receivable_qs = base_qs.filter(debt_type=Debt.TYPE_OWED_TO_ME)
    payable_original = _sum_amount(payable_qs, 'original_amount')
    receivable_original = _sum_amount(receivable_qs, 'original_amount')
    payable_remaining = _sum_amount(payable_qs, 'remaining_amount')
    receivable_remaining = _sum_amount(receivable_qs, 'remaining_amount')
    payable_paid = payable_original - payable_remaining
    receivable_collected = receivable_original - receivable_remaining

    return render(
        request,
        'debts/debt_list.html',
        {
            'debts': debts,
            'payable_remaining': _format_money(payable_remaining, currency),
            'receivable_remaining': _format_money(receivable_remaining, currency),
            'payable_paid': _format_money(payable_paid, currency),
            'receivable_collected': _format_money(receivable_collected, currency),
        },
    )


@login_required
def debt_detail(request, debt_id):
    profile = _get_profile(request.user)
    debt = get_object_or_404(Debt, debt_id=debt_id, user=profile)
    sync_debt_status_and_alert(debt)
    currency = profile.default_currency or 'VND'
    payments = debt.payments.select_related('bank_account').order_by('-payment_date', '-debt_payment_id')
    for payment in payments:
        payment.formatted_amount = _format_money(payment.amount, currency)
    labels = _debt_labels(debt)
    return render(
        request,
        'debts/debt_detail.html',
        {
            'debt': debt,
            'payments': payments,
            'formatted_original': _format_money(debt.original_amount, currency),
            'formatted_remaining': _format_money(debt.remaining_amount, currency),
            'formatted_paid': _format_money(debt.original_amount - debt.remaining_amount, currency),
            'can_add_payment': _can_add_payment(debt),
            **labels,
        },
    )


@login_required
def debt_create(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = profile
            debt.remaining_amount = debt.original_amount
            debt.save()
            sync_debt_status_and_alert(debt)
            messages.success(request, 'Đã thêm khoản nợ.')
            return redirect('debt_list')
    else:
        form = DebtForm()
    return render(request, 'debts/debt_form.html', {'form': form, 'page_title': 'Thêm khoản nợ', 'submit_label': 'Lưu khoản nợ'})


@login_required
def debt_payment_create(request, debt_id):
    profile = _get_profile(request.user)
    debt = get_object_or_404(Debt, debt_id=debt_id, user=profile)
    labels = _debt_labels(debt)
    if not _can_add_payment(debt):
        messages.warning(request, 'Khoản này đã hoàn tất hoặc đã ngừng theo dõi nên không thể ghi nhận thêm.')
        return redirect('debt_detail', debt_id=debt.debt_id)
    active_accounts = BankAccount.objects.filter(user=profile, is_active=True)
    if not active_accounts.exists():
        messages.warning(request, 'Bạn cần thêm một tài khoản đang dùng trước khi ghi nhận khoản này.')
        return redirect('bank_account_create')
    if request.method == 'POST':
        form = DebtPaymentForm(request.POST, user_profile=profile, debt=debt)
        if form.is_valid():
            payment = form.save(commit=False)
            is_full_payment = payment.amount == debt.remaining_amount
            try:
                with transaction.atomic():
                    payment.debt = debt
                    payment.save()
                    if _database_handles_debt_updates():
                        debt.refresh_from_db()
                    else:
                        debt.remaining_amount = max(Decimal('0'), debt.remaining_amount - payment.amount)
                        debt.save(update_fields=['remaining_amount', 'updated_at'])
                    sync_debt_status_and_alert(debt)
                    delta = -payment.amount if debt.debt_type == Debt.TYPE_I_OWE else payment.amount
                    BankAccount.objects.filter(
                        bank_account_id=payment.bank_account_id,
                        user=profile,
                    ).update(current_balance=F('current_balance') + delta)
            except DatabaseError:
                form.add_error(None, 'Khoản này hiện không thể ghi nhận. Hãy kiểm tra trạng thái hoặc tài khoản đã chọn.')
            else:
                success_message = labels['success_full'] if is_full_payment else labels['success_partial']
                messages.success(request, success_message)
                return redirect('debt_detail', debt_id=debt.debt_id)
    else:
        form = DebtPaymentForm(user_profile=profile, debt=debt, initial={'payment_date': timezone.now().date()})
    currency = profile.default_currency or 'VND'
    formatted_remaining = _format_money(debt.remaining_amount, currency)
    return render(
        request,
        'debts/debt_payment_form.html',
        {
            'form': form,
            'debt': debt,
            **labels,
            'formatted_original': _format_money(debt.original_amount, currency),
            'formatted_paid': _format_money(debt.original_amount - debt.remaining_amount, currency),
            'formatted_remaining': formatted_remaining,
            'remaining_amount_raw': f'{debt.remaining_amount:.2f}',
            'payoff_copy': labels['payoff_copy'].format(amount=formatted_remaining),
            'partial_copy': labels['partial_copy'],
            'warning_text': labels['warning_text'].format(amount=formatted_remaining),
        },
    )
