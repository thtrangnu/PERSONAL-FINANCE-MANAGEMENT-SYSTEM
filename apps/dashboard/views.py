from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.alerts.models import Alert
from apps.accounts.models import UserProfile
from apps.bank_accounts.models import BankAccount
from apps.budgets.models import Budget
from apps.expenses.models import Expense
from apps.income.models import Income


def _month_range(today):
    start_date = today.replace(day=1)
    if today.month == 12:
        end_date = today.replace(year=today.year + 1, month=1, day=1)
    else:
        end_date = today.replace(month=today.month + 1, day=1)
    return start_date, end_date


def _sum_amount(queryset, field_name):
    return queryset.aggregate(total=Sum(field_name))['total'] or 0


def _format_money(amount, currency='VND'):
    if currency == 'VND':
        return f'{amount:,.0f} {currency}'.replace(',', '.')
    return f'{amount:,.2f} {currency}'


def _percent(part, total):
    if not total:
        return 0
    return min(100, max(0, int((part / total) * 100)))


def _get_finance_profile(user):
    if hasattr(user, 'default_currency') and hasattr(user, 'user_id'):
        return user

    username = getattr(user, 'username', '') or 'user'
    email = getattr(user, 'email', '') or f'{username}@example.local'

    profile = UserProfile.objects.filter(username=username).first()
    if profile is None:
        profile = UserProfile.objects.filter(email=email).first()
    if profile is not None:
        return profile

    get_full_name = getattr(user, 'get_full_name', None)
    full_name = get_full_name() if callable(get_full_name) else ''

    return UserProfile.objects.create(
        username=username,
        email=email,
        password_hash=getattr(user, 'password', ''),
        full_name=full_name or username,
        role=UserProfile.ROLE_ADMIN if getattr(user, 'is_staff', False) else UserProfile.ROLE_USER,
        is_active=getattr(user, 'is_active', True),
    )


def _is_admin_user(auth_user, finance_profile):
    return (
        getattr(auth_user, 'is_staff', False)
        or getattr(auth_user, 'is_superuser', False)
        or finance_profile.role == UserProfile.ROLE_ADMIN
    )


def landing(request):
    return render(request, 'dashboard/landing.html')


def legal_policy(request):
    return render(request, 'dashboard/legal_policy.html')


def user_policy(request):
    return render(request, 'dashboard/user_policy.html')


def healthz(request):
    return JsonResponse({'status': 'ok', 'service': 'nufi'})


def metrics(request):
    active_income = Income.objects.filter(status=Income.STATUS_ACTIVE).count()
    active_expenses = Expense.objects.filter(status=Expense.STATUS_ACTIVE).count()
    unread_alerts = Alert.objects.filter(is_read=False).count()
    active_accounts = BankAccount.objects.filter(is_active=True).count()
    active_budgets = Budget.objects.filter(status=Budget.STATUS_ACTIVE).count()

    body = '\n'.join(
        [
            '# HELP nufi_up NUFI application health status.',
            '# TYPE nufi_up gauge',
            'nufi_up 1',
            '# HELP nufi_active_income_total Active income records.',
            '# TYPE nufi_active_income_total gauge',
            f'nufi_active_income_total {active_income}',
            '# HELP nufi_active_expenses_total Active expense records.',
            '# TYPE nufi_active_expenses_total gauge',
            f'nufi_active_expenses_total {active_expenses}',
            '# HELP nufi_unread_alerts_total Unread alerts.',
            '# TYPE nufi_unread_alerts_total gauge',
            f'nufi_unread_alerts_total {unread_alerts}',
            '# HELP nufi_active_accounts_total Active bank accounts.',
            '# TYPE nufi_active_accounts_total gauge',
            f'nufi_active_accounts_total {active_accounts}',
            '# HELP nufi_active_budgets_total Active budgets.',
            '# TYPE nufi_active_budgets_total gauge',
            f'nufi_active_budgets_total {active_budgets}',
            '',
        ]
    )
    return HttpResponse(body, content_type='text/plain; version=0.0.4; charset=utf-8')


@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start, next_month_start = _month_range(today)
    user = _get_finance_profile(request.user)
    currency = user.default_currency or 'VND'

    monthly_income = _sum_amount(
        Income.objects.filter(
            user=user,
            status=Income.STATUS_ACTIVE,
            income_date__gte=month_start,
            income_date__lt=next_month_start,
        ),
        'amount',
    )
    monthly_expense = _sum_amount(
        Expense.objects.filter(
            user=user,
            status=Expense.STATUS_ACTIVE,
            expense_date__gte=month_start,
            expense_date__lt=next_month_start,
        ),
        'amount',
    )
    current_balance = _sum_amount(
        BankAccount.objects.filter(user=user, is_active=True),
        'current_balance',
    )
    budget_limit = _sum_amount(
        Budget.objects.filter(
            user=user,
            status=Budget.STATUS_ACTIVE,
            period_month=today.month,
            period_year=today.year,
        ),
        'spending_limit',
    )
    budget_remaining = budget_limit - monthly_expense if budget_limit else 0
    unread_alert_count = Alert.objects.filter(user=user, is_read=False).count()
    net_flow = monthly_income - monthly_expense
    budget_used_percent = _percent(monthly_expense, budget_limit)
    budget_remaining_percent = 100 - budget_used_percent if budget_limit else 0
    budget_status = (
        f'Đã dùng {budget_used_percent}% ngân sách tháng này.'
        if budget_limit
        else 'Bạn chưa đặt ngân sách cho tháng này.'
    )
    max_cashflow_value = max(monthly_income, monthly_expense, abs(net_flow), 1)
    remaining_for_chart = max(budget_limit - monthly_expense, 0) if budget_limit else 0

    context = {
        'dashboard_month': f'Tháng {today.month}/{today.year}',
        'dashboard_user_name': user.full_name or user.username,
        'show_admin_shortcut': _is_admin_user(request.user, user),
        'net_flow': _format_money(net_flow, currency),
        'net_flow_label': 'Dòng tiền tháng này đang dương' if net_flow >= 0 else 'Dòng tiền tháng này đang âm',
        'budget_used_percent': budget_used_percent,
        'budget_status': budget_status,
        'alert_summary': (
            f'Bạn có {unread_alert_count} cảnh báo chưa đọc.'
            if unread_alert_count
            else 'Hiện chưa có cảnh báo mới.'
        ),
        'dashboard_cards': [
            {
                'order': '01',
                'label': 'Tiền vào tháng này',
                'value': _format_money(monthly_income, currency),
                'note': 'Tổng các khoản tiền đã ghi nhận trong tháng.',
            },
            {
                'order': '02',
                'label': 'Tiền ra tháng này',
                'value': _format_money(monthly_expense, currency),
                'note': 'Tổng các khoản đã chi trong tháng hiện tại.',
            },
            {
                'order': '03',
                'label': 'Số tiền hiện có',
                'value': _format_money(current_balance, currency),
                'note': 'Tổng số dư của các tài khoản đang theo dõi.',
            },
            {
                'order': '04',
                'label': 'Ngân sách còn lại',
                'value': _format_money(budget_remaining, currency),
                'note': 'Số tiền còn lại sau khi trừ chi tiêu tháng này.',
            },
            {
                'order': '05',
                'label': 'Cảnh báo chưa đọc',
                'value': unread_alert_count,
                'note': 'Các nhắc nhở bạn chưa xem trong hệ thống.',
            },
        ],
        'summary_rows': [
            {
                'label': 'Tổng tiền vào',
                'value': _format_money(monthly_income, currency),
                'explain': 'Các khoản thu đang hoạt động trong tháng hiện tại.',
            },
            {
                'label': 'Tổng tiền ra',
                'value': _format_money(monthly_expense, currency),
                'explain': 'Các khoản chi đang hoạt động trong tháng hiện tại.',
            },
            {
                'label': 'Dòng tiền ròng',
                'value': _format_money(net_flow, currency),
                'explain': 'Tiền vào trừ tiền ra trong tháng.',
            },
            {
                'label': 'Ngân sách đã đặt',
                'value': _format_money(budget_limit, currency),
                'explain': 'Tổng ngân sách đang hoạt động của tháng này.',
            },
            {
                'label': 'Ngân sách còn lại',
                'value': _format_money(budget_remaining, currency),
                'explain': 'Ngân sách đã đặt trừ tổng chi tiêu tháng này.',
            },
        ],
        'cashflow_bars': [
            {
                'label': 'Tiền vào',
                'value': _format_money(monthly_income, currency),
                'percent': _percent(monthly_income, max_cashflow_value),
                'tone': 'income',
            },
            {
                'label': 'Tiền ra',
                'value': _format_money(monthly_expense, currency),
                'percent': _percent(monthly_expense, max_cashflow_value),
                'tone': 'expense',
            },
            {
                'label': 'Dòng tiền ròng',
                'value': _format_money(net_flow, currency),
                'percent': _percent(abs(net_flow), max_cashflow_value),
                'tone': 'net-positive' if net_flow >= 0 else 'net-negative',
            },
        ],
        'budget_chart_available': bool(budget_limit),
        'budget_chart_center': f'{budget_used_percent}%',
        'budget_segments': [
            {
                'label': 'Đã chi',
                'value': _format_money(monthly_expense, currency),
                'percent': budget_used_percent,
                'offset': 0,
                'class_name': 'spent',
            },
            {
                'label': 'Còn lại',
                'value': _format_money(remaining_for_chart, currency),
                'percent': budget_remaining_percent,
                'offset': -budget_used_percent,
                'class_name': 'remaining',
            },
        ],
        'budget_chart_note': (
            f'Tổng ngân sách tháng này: {_format_money(budget_limit, currency)}.'
            if budget_limit
            else 'Chưa có dữ liệu ngân sách để vẽ chart.'
        ),
    }
    return render(request, 'dashboard/dashboard.html', context)
