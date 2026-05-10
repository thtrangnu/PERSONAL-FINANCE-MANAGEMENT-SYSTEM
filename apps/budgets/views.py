from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.models import UserProfile
from apps.budgets.forms import BudgetForm
from apps.budgets.models import Budget
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


def _wants_json(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _format_money(amount, currency='VND'):
    amount = amount or 0
    if currency == 'VND':
        return f'{amount:,.0f} {currency}'.replace(',', '.')
    return f'{amount:,.2f} {currency}'


def _month_range(year, month):
    start_date = timezone.datetime(year=year, month=month, day=1).date()
    if month == 12:
        next_month = timezone.datetime(year=year + 1, month=1, day=1).date()
    else:
        next_month = timezone.datetime(year=year, month=month + 1, day=1).date()
    return start_date, next_month


def _attach_usage(budgets, currency):
    for budget in budgets:
        start_date, next_month = _month_range(budget.period_year, budget.period_month)
        expense_filter = {
            'user': budget.user,
            'status': Expense.STATUS_ACTIVE,
            'expense_date__gte': start_date,
            'expense_date__lt': next_month,
        }
        if budget.budget_scope == Budget.SCOPE_CATEGORY:
            expense_filter['category'] = budget.category
        used_amount = Expense.objects.filter(**expense_filter).aggregate(total=Sum('amount'))['total'] or 0
        remaining_amount = budget.spending_limit - used_amount
        percent = int((used_amount / budget.spending_limit) * 100) if budget.spending_limit else 0
        budget.used_amount = _format_money(used_amount, currency)
        budget.remaining_amount = _format_money(remaining_amount, currency)
        budget.usage_percent = min(100, max(0, percent))
        if percent >= 100:
            budget.progress_class = 'is-exceeded'
        elif percent >= int(budget.warning_percent):
            budget.progress_class = 'is-warning'
        else:
            budget.progress_class = ''
    return budgets


@login_required
def budget_list(request):
    profile = _get_profile(request.user)
    budgets = list(
        Budget.objects.filter(user=profile)
        .select_related('category')
        .order_by('-period_year', '-period_month', 'budget_name')
    )
    _attach_usage(budgets, profile.default_currency or 'VND')

    return render(
        request,
        'budgets/budget_list.html',
        {'budgets': budgets},
    )


@login_required
def budget_create(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, user_profile=profile)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = profile
            if budget.budget_scope == Budget.SCOPE_OVERALL:
                budget.category = None
            budget.save()
            messages.success(request, 'Đã tạo ngân sách.')
            return redirect('budget_list')
    else:
        today = timezone.now().date()
        form = BudgetForm(
            user_profile=profile,
            initial={
                'period_month': today.month,
                'period_year': today.year,
                'budget_scope': Budget.SCOPE_OVERALL,
            },
        )

    return render(
        request,
        'budgets/budget_form.html',
        {'form': form, 'page_title': 'Tạo ngân sách', 'submit_label': 'Lưu ngân sách'},
    )


@login_required
def budget_update(request, budget_id):
    profile = _get_profile(request.user)
    budget = get_object_or_404(Budget, budget_id=budget_id, user=profile)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user_profile=profile)
        if form.is_valid():
            budget = form.save(commit=False)
            if budget.budget_scope == Budget.SCOPE_OVERALL:
                budget.category = None
            budget.save()
            messages.success(request, 'Đã cập nhật ngân sách.')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user_profile=profile)

    return render(
        request,
        'budgets/budget_form.html',
        {'form': form, 'page_title': 'Sửa ngân sách', 'submit_label': 'Lưu thay đổi'},
    )


@login_required
def budget_delete(request, budget_id):
    profile = _get_profile(request.user)
    budget = get_object_or_404(Budget, budget_id=budget_id, user=profile)

    if request.method == 'POST':
        budget.status = Budget.STATUS_CLOSED
        budget.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Đã đóng ngân sách.')
        return redirect('budget_list')

    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})


@login_required
@require_POST
def budget_toggle_status(request, budget_id):
    profile = _get_profile(request.user)
    budget = get_object_or_404(Budget, budget_id=budget_id, user=profile)
    if budget.status == Budget.STATUS_CLOSED:
        message = 'Ngân sách đã đóng nên không thể bật/tắt nhanh.'
        if _wants_json(request):
            return JsonResponse(
                {
                    'ok': False,
                    'is_on': False,
                    'label': 'Đã đóng',
                    'message': message,
                },
                status=400,
            )
        messages.info(request, message)
    elif budget.status == Budget.STATUS_ACTIVE:
        budget.status = Budget.STATUS_INACTIVE
        budget.save(update_fields=['status', 'updated_at'])
        message = 'Đã tạm tắt ngân sách.'
    else:
        budget.status = Budget.STATUS_ACTIVE
        budget.save(update_fields=['status', 'updated_at'])
        message = 'Đã bật lại ngân sách.'

    if _wants_json(request):
        return JsonResponse(
            {
                'ok': True,
                'is_on': budget.status == Budget.STATUS_ACTIVE,
                'label': 'Đang dùng' if budget.status == Budget.STATUS_ACTIVE else 'Tạm tắt',
                'message': message,
            }
        )

    messages.success(request, message)

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('budget_list')
