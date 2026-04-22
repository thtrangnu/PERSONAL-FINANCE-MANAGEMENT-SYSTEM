from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.models import UserProfile
from apps.alerts.models import Alert
from apps.sharing.models import GroupMember


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


@login_required
def alert_list(request):
    profile = _get_profile(request.user)
    show = request.GET.get('show', 'all')
    alerts = Alert.objects.filter(user=profile).select_related('related_budget', 'related_expense')
    if show == 'unread':
        alerts = alerts.filter(is_read=False)
    alerts = alerts.order_by('-created_at', '-alert_id')
    pending_invitations = (
        GroupMember.objects.filter(user=profile, status=GroupMember.STATUS_PENDING)
        .select_related('group', 'group__owner_user')
        .order_by('-joined_at')
    )

    return render(
        request,
        'alerts/alert_list.html',
        {
            'alerts': alerts,
            'pending_invitations': pending_invitations,
            'show': show,
            'unread_count': Alert.objects.filter(user=profile, is_read=False).count() + pending_invitations.count(),
        },
    )


@login_required
@require_POST
def alert_mark_read(request, alert_id):
    profile = _get_profile(request.user)
    alert = get_object_or_404(Alert, alert_id=alert_id, user=profile)
    alert.is_read = True
    alert.save(update_fields=['is_read'])
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    messages.success(request, 'Đã đánh dấu cảnh báo là đã đọc.')
    return redirect('alert_list')
