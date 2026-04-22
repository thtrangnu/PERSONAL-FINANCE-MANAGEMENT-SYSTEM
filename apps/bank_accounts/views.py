from decimal import Decimal
from math import cos, radians, sin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.models import UserProfile
from apps.bank_accounts.forms import BankAccountForm
from apps.bank_accounts.models import BankAccount
from apps.expenses.models import Expense
from apps.income.models import Income


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


def _format_percent(value):
    formatted = f'{value:.1f}'
    if formatted.endswith('.0'):
        formatted = formatted[:-2]
    return f'{formatted}%'


def _circle_point(radius, angle_degrees):
    angle = radians(angle_degrees)
    return 70 + radius * cos(angle), 70 + radius * sin(angle)


def _donut_segment_path(start_percent, percent):
    outer_radius = 58
    inner_radius = 30
    safe_percent = min(max(float(percent), 0.01), 99.999)
    start_angle = (float(start_percent) / 100 * 360) - 90
    end_angle = start_angle + (safe_percent / 100 * 360)
    large_arc = 1 if end_angle - start_angle > 180 else 0

    outer_start = _circle_point(outer_radius, start_angle)
    outer_end = _circle_point(outer_radius, end_angle)
    inner_end = _circle_point(inner_radius, end_angle)
    inner_start = _circle_point(inner_radius, start_angle)

    return (
        f'M {outer_start[0]:.3f} {outer_start[1]:.3f} '
        f'A {outer_radius} {outer_radius} 0 {large_arc} 1 {outer_end[0]:.3f} {outer_end[1]:.3f} '
        f'L {inner_end[0]:.3f} {inner_end[1]:.3f} '
        f'A {inner_radius} {inner_radius} 0 {large_arc} 0 {inner_start[0]:.3f} {inner_start[1]:.3f} Z'
    )


def _build_category_breakdown(queryset, total_amount, currency):
    if not total_amount:
        return []

    rows = queryset.values('category__category_name').annotate(total=Sum('amount')).order_by('-total')
    breakdown = []
    offset = Decimal('0')

    for index, row in enumerate(rows):
        amount = row['total'] or Decimal('0')
        percent_value = (Decimal(amount) / Decimal(total_amount)) * Decimal('100')
        percent = round(float(percent_value), 1)
        breakdown.append(
            {
                'label': row['category__category_name'] or 'Chưa phân loại',
                'value': _format_money(amount, currency),
                'percent': percent,
                'percent_label': _format_percent(percent),
                'offset': round(float(-offset), 1),
                'path_d': _donut_segment_path(offset, percent_value),
                'class_name': f'slice-{(index % 8) + 1}',
            }
        )
        offset += percent_value

    return breakdown


def _wants_json(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _active_account_summary(profile):
    active_accounts = BankAccount.objects.filter(user=profile, is_active=True)
    total_balance = active_accounts.aggregate(total=Sum('current_balance'))['total'] or 0
    return {
        'active_account_count': active_accounts.count(),
        'total_balance': _format_money(total_balance, profile.default_currency or 'VND'),
    }


@login_required
def bank_account_list(request):
    profile = _get_profile(request.user)
    accounts = BankAccount.objects.filter(user=profile).order_by('-is_active', 'account_name')
    summary = _active_account_summary(profile)
    for account in accounts:
        account.formatted_current_balance = _format_money(account.current_balance, account.currency)

    return render(
        request,
        'bank_accounts/account_list.html',
        {
            'accounts': accounts,
            'active_account_count': summary['active_account_count'],
            'total_balance': summary['total_balance'],
        },
    )


@login_required
def bank_account_detail(request, bank_account_id):
    profile = _get_profile(request.user)
    account = get_object_or_404(BankAccount, bank_account_id=bank_account_id, user=profile)
    income_queryset = Income.objects.filter(
        user=profile,
        bank_account=account,
        status=Income.STATUS_ACTIVE,
    )
    expense_queryset = Expense.objects.filter(
        user=profile,
        bank_account=account,
        status=Expense.STATUS_ACTIVE,
    )

    total_income = income_queryset.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expense_queryset.aggregate(total=Sum('amount'))['total'] or 0
    income_breakdown = _build_category_breakdown(income_queryset, total_income, account.currency)
    expense_breakdown = _build_category_breakdown(expense_queryset, total_expense, account.currency)
    incomes = list(income_queryset.select_related('category').order_by('-income_date', '-income_id'))
    expenses = list(expense_queryset.select_related('category').order_by('-expense_date', '-expense_id'))

    for income in incomes:
        income.formatted_amount = _format_money(income.amount, account.currency)
    for expense in expenses:
        expense.formatted_amount = _format_money(expense.amount, account.currency)

    return render(
        request,
        'bank_accounts/account_detail.html',
        {
            'account': account,
            'incomes': incomes,
            'expenses': expenses,
            'total_income': _format_money(total_income, account.currency),
            'total_expense': _format_money(total_expense, account.currency),
            'net_flow': _format_money(total_income - total_expense, account.currency),
            'current_balance': _format_money(account.current_balance, account.currency),
            'opening_balance': _format_money(account.opening_balance, account.currency),
            'income_breakdown': income_breakdown,
            'expense_breakdown': expense_breakdown,
        },
    )


@login_required
def bank_account_create(request):
    profile = _get_profile(request.user)

    if request.method == 'POST':
        form = BankAccountForm(request.POST, show_balance_split=False)
        if form.is_valid():
            with transaction.atomic():
                account = form.save(commit=False)
                initial_balance = account.opening_balance or Decimal('0')
                account.user = profile
                account.currency = profile.default_currency or 'VND'
                account.current_balance = Decimal('0')
                account.save()
                BankAccount.objects.filter(bank_account_id=account.bank_account_id).update(
                    current_balance=initial_balance,
                )
            messages.success(request, 'Đã thêm tài khoản tiền.')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm(show_balance_split=False)

    return render(
        request,
        'bank_accounts/account_form.html',
        {
            'form': form,
            'page_title': 'Thêm tài khoản tiền',
            'form_intro': 'Nhập số dư hiện có của tài khoản. Sau khi tài khoản được dùng, NUFI sẽ theo dõi riêng số dư ban đầu và số dư hiện tại cho bạn.',
            'submit_label': 'Lưu tài khoản',
        },
    )


@login_required
def bank_account_update(request, bank_account_id):
    profile = _get_profile(request.user)
    account = get_object_or_404(BankAccount, bank_account_id=bank_account_id, user=profile)

    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật tài khoản tiền.')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm(instance=account)

    return render(
        request,
        'bank_accounts/account_form.html',
        {
            'form': form,
            'page_title': 'Sửa tài khoản tiền',
            'form_intro': 'Điều chỉnh thông tin tài khoản và theo dõi riêng số dư ban đầu với số dư hiện tại.',
            'submit_label': 'Lưu thay đổi',
        },
    )


@login_required
def bank_account_delete(request, bank_account_id):
    profile = _get_profile(request.user)
    account = get_object_or_404(BankAccount, bank_account_id=bank_account_id, user=profile)

    if request.method == 'POST':
        account.is_active = False
        account.save(update_fields=['is_active', 'updated_at'])
        messages.success(request, 'Đã ngừng theo dõi tài khoản tiền.')
        return redirect('bank_account_list')

    return render(
        request,
        'bank_accounts/account_confirm_delete.html',
        {'account': account},
    )


@login_required
@require_POST
def bank_account_toggle_status(request, bank_account_id):
    profile = _get_profile(request.user)
    account = get_object_or_404(BankAccount, bank_account_id=bank_account_id, user=profile)
    account.is_active = not account.is_active
    account.save(update_fields=['is_active', 'updated_at'])

    if account.is_active:
        message = 'Đã bật lại tài khoản tiền.'
    else:
        message = 'Đã tắt tài khoản tiền.'

    if _wants_json(request):
        return JsonResponse(
            {
                'ok': True,
                'is_on': account.is_active,
                'label': 'Đang dùng' if account.is_active else 'Đã tắt',
                'message': message,
                **_active_account_summary(profile),
            }
        )

    messages.success(request, message)

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('bank_account_list')
