from decimal import Decimal
from math import cos, radians, sin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.alerts.models import Alert
from apps.bank_accounts.balance import adjust_balance
from apps.bank_accounts.models import BankAccount
from apps.budgets.models import Budget
from apps.categories.models import ExpenseCategory
from apps.expenses.forms import ExpenseForm
from apps.expenses.models import Expense


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


def _month_range(expense_date):
    start_date = expense_date.replace(day=1)
    if expense_date.month == 12:
        next_month = expense_date.replace(year=expense_date.year + 1, month=1, day=1)
    else:
        next_month = expense_date.replace(month=expense_date.month + 1, day=1)
    return start_date, next_month


def _adjust_balance(account_id, amount_delta):
    adjust_balance(
        account_id,
        amount_delta,
        trigger_names=('trg_expenses_ai_update_balance', 'trg_expenses_au_update_balance'),
    )


def _create_budget_alerts(expense):
    month_start, next_month = _month_range(expense.expense_date)
    budgets = Budget.objects.filter(
        user=expense.user,
        status=Budget.STATUS_ACTIVE,
        period_month=expense.expense_date.month,
        period_year=expense.expense_date.year,
    )

    for budget in budgets:
        expense_filter = {
            'user': expense.user,
            'status': Expense.STATUS_ACTIVE,
            'expense_date__gte': month_start,
            'expense_date__lt': next_month,
        }
        if budget.budget_scope == Budget.SCOPE_CATEGORY:
            if budget.category_id != expense.category_id:
                continue
            expense_filter['category'] = budget.category

        used_amount = Expense.objects.filter(**expense_filter).aggregate(total=Sum('amount'))['total'] or 0
        if not budget.spending_limit:
            continue

        usage_percent = (Decimal(used_amount) / Decimal(budget.spending_limit)) * Decimal('100')
        if used_amount >= budget.spending_limit:
            alert_type = Alert.TYPE_BUDGET_EXCEEDED
            severity = Alert.SEVERITY_CRITICAL
            title = 'Đã vượt ngân sách'
            message = f'Bạn đã chi {_format_money(used_amount, expense.user.default_currency or "VND")} cho {budget.budget_name}.'
        elif usage_percent >= budget.warning_percent:
            alert_type = Alert.TYPE_BUDGET_WARNING
            severity = Alert.SEVERITY_WARNING
            title = 'Sắp chạm ngân sách'
            message = f'Bạn đã dùng {usage_percent:.0f}% ngân sách {budget.budget_name}.'
        else:
            continue

        already_exists = Alert.objects.filter(
            user=expense.user,
            related_budget=budget,
            related_expense=expense,
            alert_type=alert_type,
        ).exists()
        if already_exists:
            continue

        Alert.objects.create(
            user=expense.user,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            related_budget=budget,
            related_expense=expense,
        )


@login_required
def expense_list(request):
    profile = _get_profile(request.user)
    expenses = Expense.objects.filter(user=profile, status=Expense.STATUS_ACTIVE).select_related('category', 'bank_account')

    start_date = request.GET.get('start_date') or ''
    end_date = request.GET.get('end_date') or ''
    category_id = request.GET.get('category') or ''
    bank_account_id = request.GET.get('bank_account') or ''
    if start_date:
        expenses = expenses.filter(expense_date__gte=start_date)
    if end_date:
        expenses = expenses.filter(expense_date__lte=end_date)
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if bank_account_id:
        expenses = expenses.filter(bank_account_id=bank_account_id)

    filtered_expenses = expenses
    currency = profile.default_currency or 'VND'
    total_expense = filtered_expenses.aggregate(total=Sum('amount'))['total'] or 0
    expense_breakdown = _build_category_breakdown(filtered_expenses, total_expense, currency)

    expenses = filtered_expenses.order_by('-expense_date', '-expense_id')
    for expense in expenses:
        expense.formatted_amount = _format_money(expense.amount, currency)

    return render(
        request,
        'expenses/expense_list.html',
        {
            'expenses': expenses,
            'categories': ExpenseCategory.objects.filter(
                Q(user=profile) | Q(user__isnull=True),
                category_type__in=[ExpenseCategory.TYPE_EXPENSE, ExpenseCategory.TYPE_BOTH],
                is_active=True,
            ).order_by('category_name'),
            'bank_accounts': BankAccount.objects.filter(user=profile, is_active=True).order_by('account_name'),
            'total_expense': _format_money(total_expense, currency),
            'expense_breakdown': expense_breakdown,
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'category': category_id,
                'bank_account': bank_account_id,
            },
        },
    )


@login_required
def expense_create(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user_profile=profile)
        if form.is_valid():
            with transaction.atomic():
                expense = form.save(commit=False)
                expense.user = profile
                expense.status = Expense.STATUS_ACTIVE
                expense.save()
                _adjust_balance(expense.bank_account_id, -expense.amount)
                _create_budget_alerts(expense)
            messages.success(request, 'Đã thêm khoản chi tiêu.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user_profile=profile, initial={'expense_date': timezone.now().date()})

    return render(
        request,
        'expenses/expense_form.html',
        {'form': form, 'page_title': 'Thêm chi tiêu', 'submit_label': 'Lưu khoản chi'},
    )


@login_required
def expense_update(request, expense_id):
    profile = _get_profile(request.user)
    expense = get_object_or_404(Expense, expense_id=expense_id, user=profile, status=Expense.STATUS_ACTIVE)
    old_account_id = expense.bank_account_id
    old_amount = expense.amount

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user_profile=profile)
        if form.is_valid():
            with transaction.atomic():
                updated_expense = form.save(commit=False)
                updated_expense.user = profile
                updated_expense.status = Expense.STATUS_ACTIVE
                updated_expense.save()
                _adjust_balance(old_account_id, old_amount)
                _adjust_balance(updated_expense.bank_account_id, -updated_expense.amount)
                _create_budget_alerts(updated_expense)
            messages.success(request, 'Đã cập nhật khoản chi tiêu.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user_profile=profile)

    return render(
        request,
        'expenses/expense_form.html',
        {'form': form, 'page_title': 'Sửa chi tiêu', 'submit_label': 'Lưu thay đổi'},
    )


@login_required
def expense_delete(request, expense_id):
    profile = _get_profile(request.user)
    expense = get_object_or_404(Expense, expense_id=expense_id, user=profile, status=Expense.STATUS_ACTIVE)

    if request.method == 'POST':
        with transaction.atomic():
            _adjust_balance(expense.bank_account_id, expense.amount)
            expense.status = Expense.STATUS_DELETED
            expense.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Đã xóa khoản chi tiêu.')
        return redirect('expense_list')

    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})
