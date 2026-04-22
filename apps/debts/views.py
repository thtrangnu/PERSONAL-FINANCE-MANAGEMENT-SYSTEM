from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection, transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import UserProfile
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


def _can_add_payment(debt):
    return debt.is_active and debt.status != Debt.STATUS_PAID and debt.remaining_amount > 0


@login_required
def debt_list(request):
    profile = _get_profile(request.user)
    debts = Debt.objects.filter(user=profile).order_by('-is_active', 'due_date', '-debt_id')
    total_original = debts.aggregate(total=Sum('original_amount'))['total'] or 0
    total_remaining = debts.aggregate(total=Sum('remaining_amount'))['total'] or 0
    total_paid = total_original - total_remaining
    currency = profile.default_currency or 'VND'

    for debt in debts:
        sync_debt_status_and_alert(debt)
        debt.formatted_original = _format_money(debt.original_amount, currency)
        debt.formatted_remaining = _format_money(debt.remaining_amount, currency)
        debt.can_add_payment = _can_add_payment(debt)

    return render(
        request,
        'debts/debt_list.html',
        {
            'debts': debts,
            'total_debt': _format_money(total_original, currency),
            'total_paid': _format_money(total_paid, currency),
            'total_remaining': _format_money(total_remaining, currency),
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
    if not _can_add_payment(debt):
        messages.warning(request, 'Khoản nợ này đã hoàn tất hoặc đã ngừng theo dõi nên không thể thêm thanh toán.')
        return redirect('debt_detail', debt_id=debt.debt_id)
    active_accounts = BankAccount.objects.filter(user=profile, is_active=True)
    if not active_accounts.exists():
        messages.warning(request, 'Bạn cần thêm một tài khoản đang dùng trước khi ghi nhận thanh toán nợ.')
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
                    if connection.vendor == 'mysql':
                        debt.refresh_from_db()
                    else:
                        debt.remaining_amount = max(Decimal('0'), debt.remaining_amount - payment.amount)
                    sync_debt_status_and_alert(debt)
                    delta = -payment.amount if debt.debt_type == Debt.TYPE_I_OWE else payment.amount
                    BankAccount.objects.filter(
                        bank_account_id=payment.bank_account_id,
                        user=profile,
                    ).update(current_balance=F('current_balance') + delta)
            except DatabaseError:
                form.add_error(None, 'Khoản nợ này hiện không thể ghi nhận thanh toán. Hãy kiểm tra trạng thái khoản nợ hoặc tài khoản thanh toán.')
            else:
                success_message = 'Đã tất toán khoản nợ.' if is_full_payment else 'Đã ghi nhận thanh toán một phần.'
                messages.success(request, success_message)
                return redirect('debt_detail', debt_id=debt.debt_id)
    else:
        form = DebtPaymentForm(user_profile=profile, debt=debt, initial={'payment_date': timezone.now().date()})
    currency = profile.default_currency or 'VND'
    return render(
        request,
        'debts/debt_payment_form.html',
        {
            'form': form,
            'debt': debt,
            'page_title': 'Thêm lần thanh toán',
            'submit_label': 'Lưu thanh toán',
            'formatted_original': _format_money(debt.original_amount, currency),
            'formatted_paid': _format_money(debt.original_amount - debt.remaining_amount, currency),
            'formatted_remaining': _format_money(debt.remaining_amount, currency),
            'remaining_amount_raw': f'{debt.remaining_amount:.2f}',
        },
    )
