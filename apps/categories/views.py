from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.models import UserProfile
from apps.categories.forms import CategoryForm
from apps.categories.models import ExpenseCategory


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


@login_required
def category_list(request):
    profile = _get_profile(request.user)
    user_categories = ExpenseCategory.objects.filter(user=profile).order_by('-is_active', 'category_name')
    default_categories = ExpenseCategory.objects.filter(user__isnull=True, is_active=True).order_by('category_name')

    return render(
        request,
        'categories/category_list.html',
        {
            'user_categories': user_categories,
            'default_categories': default_categories,
        },
    )


@login_required
def category_create(request):
    profile = _get_profile(request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = profile
            category.is_default = False
            try:
                category.save()
            except IntegrityError:
                form.add_error('category_name', 'Bạn đã có danh mục này rồi.')
            else:
                messages.success(request, 'Đã thêm danh mục mới.')
                return redirect('category_list')
    else:
        form = CategoryForm()

    return render(
        request,
        'categories/category_form.html',
        {
            'form': form,
            'page_title': 'Thêm danh mục',
            'submit_label': 'Lưu danh mục',
        },
    )


@login_required
def category_update(request, category_id):
    profile = _get_profile(request.user)
    category = get_object_or_404(ExpenseCategory, category_id=category_id, user=profile)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error('category_name', 'Bạn đã có danh mục này rồi.')
            else:
                messages.success(request, 'Đã cập nhật danh mục.')
                return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        'categories/category_form.html',
        {
            'form': form,
            'page_title': 'Sửa danh mục',
            'submit_label': 'Lưu thay đổi',
        },
    )


@login_required
def category_delete(request, category_id):
    profile = _get_profile(request.user)
    category = get_object_or_404(ExpenseCategory, category_id=category_id, user=profile)

    if request.method == 'POST':
        category.is_active = False
        category.save(update_fields=['is_active', 'updated_at'])
        messages.success(request, 'Đã ngừng sử dụng danh mục.')
        return redirect('category_list')

    return render(
        request,
        'categories/category_confirm_delete.html',
        {'category': category},
    )


@login_required
@require_POST
def category_toggle_status(request, category_id):
    profile = _get_profile(request.user)
    category = get_object_or_404(ExpenseCategory, category_id=category_id, user=profile)
    category.is_active = not category.is_active
    category.save(update_fields=['is_active', 'updated_at'])

    if category.is_active:
        message = 'Đã bật lại danh mục.'
    else:
        message = 'Đã tắt danh mục.'

    if _wants_json(request):
        return JsonResponse(
            {
                'ok': True,
                'is_on': category.is_active,
                'label': 'Đang dùng' if category.is_active else 'Đã tắt',
                'message': message,
            }
        )

    messages.success(request, message)

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('category_list')
