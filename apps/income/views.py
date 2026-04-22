from decimal import Decimal
from math import cos, radians, sin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.bank_accounts.balance import adjust_balance
from apps.bank_accounts.models import BankAccount
from apps.income.forms import IncomeForm
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


def _adjust_balance(account_id, amount_delta):
    adjust_balance(
        account_id,
        amount_delta,
        trigger_names=('trg_incomes_ai_update_balance', 'trg_incomes_au_update_balance'),
    )


@login_required
def income_list(request):
    profile = _get_profile(request.user)
    incomes = Income.objects.filter(user=profile, status=Income.STATUS_ACTIVE).select_related('category', 'bank_account')

    start_date = request.GET.get('start_date') or ''
    end_date = request.GET.get('end_date') or ''
    bank_account_id = request.GET.get('bank_account') or ''
    if start_date:
        incomes = incomes.filter(income_date__gte=start_date)
    if end_date:
        incomes = incomes.filter(income_date__lte=end_date)
    if bank_account_id:
        incomes = incomes.filter(bank_account_id=bank_account_id)

    filtered_incomes = incomes
    currency = profile.default_currency or 'VND'
    total_income = filtered_incomes.aggregate(total=Sum('amount'))['total'] or 0
    income_breakdown = _build_category_breakdown(filtered_incomes, total_income, currency)

    incomes = filtered_incomes.order_by('-income_date', '-income_id')
    for income in incomes:
        income.formatted_amount = _format_money(income.amount, currency)

    return render(
        request,
        'income/income_list.html',
        {
            'incomes': incomes,
            'bank_accounts': BankAccount.objects.filter(user=profile, is_active=True).order_by('account_name'),
            'total_income': _format_money(total_income, currency),
            'income_breakdown': income_breakdown,
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'bank_account': bank_account_id,
            },
        },
    )


@login_required
def income_create(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, user_profile=profile)
        if form.is_valid():
            with transaction.atomic():
                income = form.save(commit=False)
                income.user = profile
                income.status = Income.STATUS_ACTIVE
                income.save()
                _adjust_balance(income.bank_account_id, income.amount)
            messages.success(request, 'Đã thêm khoản thu nhập.')
            return redirect('income_list')
    else:
        form = IncomeForm(user_profile=profile, initial={'income_date': timezone.now().date()})

    return render(
        request,
        'income/income_form.html',
        {'form': form, 'page_title': 'Thêm thu nhập', 'submit_label': 'Lưu khoản thu'},
    )


@login_required
def income_update(request, income_id):
    profile = _get_profile(request.user)
    income = get_object_or_404(Income, income_id=income_id, user=profile, status=Income.STATUS_ACTIVE)
    old_account_id = income.bank_account_id
    old_amount = income.amount

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income, user_profile=profile)
        if form.is_valid():
            with transaction.atomic():
                updated_income = form.save(commit=False)
                updated_income.user = profile
                updated_income.status = Income.STATUS_ACTIVE
                updated_income.save()
                _adjust_balance(old_account_id, -old_amount)
                _adjust_balance(updated_income.bank_account_id, updated_income.amount)
            messages.success(request, 'Đã cập nhật khoản thu nhập.')
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income, user_profile=profile)

    return render(
        request,
        'income/income_form.html',
        {'form': form, 'page_title': 'Sửa thu nhập', 'submit_label': 'Lưu thay đổi'},
    )


@login_required
def income_delete(request, income_id):
    profile = _get_profile(request.user)
    income = get_object_or_404(Income, income_id=income_id, user=profile, status=Income.STATUS_ACTIVE)

    if request.method == 'POST':
        with transaction.atomic():
            _adjust_balance(income.bank_account_id, -income.amount)
            income.status = Income.STATUS_DELETED
            income.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Đã xóa khoản thu nhập.')
        return redirect('income_list')

    return render(request, 'income/income_confirm_delete.html', {'income': income})
