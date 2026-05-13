from functools import lru_cache

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.accounts.models import UserProfile
from apps.sharing.forms import AddMemberForm, SharedTransactionForm, SharingGroupForm
from apps.sharing.models import GroupMember, SharingGroup


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


def _member_group(profile, group_id):
    group = get_object_or_404(
        SharingGroup.objects.select_related('owner_user'),
        group_id=group_id,
    )
    if group.owner_user_id == profile.user_id:
        return group
    get_object_or_404(
        GroupMember,
        group=group,
        user=profile,
        status=GroupMember.STATUS_ACTIVE,
    )
    return group


def _wants_json(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


@lru_cache(maxsize=1)
def _ensure_pending_member_status_supported():
    if connection.vendor != 'mysql':
        return

    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM `group_members` LIKE 'status'")
            row = cursor.fetchone()
            column_type = row[1] if row else ''
            if 'pending' in column_type:
                return

            cursor.execute(
                """
                ALTER TABLE `group_members`
                MODIFY `status`
                ENUM('pending', 'active', 'left', 'removed')
                NOT NULL DEFAULT 'active'
                """
            )
    except DatabaseError:
        _ensure_pending_member_status_supported.cache_clear()
        raise


@login_required
def group_list(request):
    profile = _get_profile(request.user)
    groups = SharingGroup.objects.filter(
        Q(owner_user=profile)
        | Q(members__user=profile, members__status=GroupMember.STATUS_ACTIVE)
    ).select_related('owner_user').annotate(
        active_member_count=Count(
            'members',
            filter=Q(members__status=GroupMember.STATUS_ACTIVE),
            distinct=True,
        )
    ).distinct().order_by('-created_at')
    pending_invitations = (
        GroupMember.objects.filter(user=profile, status=GroupMember.STATUS_PENDING)
        .select_related('group', 'group__owner_user')
        .order_by('-joined_at')
    )
    for group in groups:
        group.can_toggle_status = group.owner_user_id == profile.user_id
        group.active_member_count = (
            group.members.filter(status=GroupMember.STATUS_ACTIVE)
            .exclude(user_id=group.owner_user_id)
            .values('user_id')
            .distinct()
            .count()
            + 1
        )
    return render(
        request,
        'sharing/group_list.html',
        {'groups': groups, 'pending_invitations': pending_invitations},
    )


@login_required
def group_create(request):
    profile = _get_profile(request.user)
    if request.method == 'POST':
        form = SharingGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner_user = profile
            group.save()
            GroupMember.objects.create(group=group, user=profile, member_role=GroupMember.ROLE_OWNER)
            messages.success(request, 'Đã tạo nhóm chia sẻ.')
            return redirect('sharing_group_detail', group_id=group.group_id)
    else:
        form = SharingGroupForm()
    return render(request, 'sharing/group_form.html', {'form': form, 'page_title': 'Tạo nhóm chia sẻ', 'submit_label': 'Tạo nhóm'})


@login_required
def group_detail(request, group_id):
    profile = _get_profile(request.user)
    group = _member_group(profile, group_id)
    active_memberships = list(
        group.members.select_related('user')
        .filter(status=GroupMember.STATUS_ACTIVE)
        .exclude(user_id=group.owner_user_id)
        .order_by('member_role', 'joined_at')
    )
    members = [
        {
            'name': group.owner_user.full_name or group.owner_user.username,
            'role_label': 'Chủ nhóm',
        }
    ]
    members.extend(
        {
            'name': membership.user.full_name or membership.user.username,
            'role_label': membership.get_member_role_display(),
        }
        for membership in active_memberships
    )
    pending_members = group.members.select_related('user').filter(status=GroupMember.STATUS_PENDING).order_by('-joined_at')
    transactions = group.shared_transactions.select_related(
        'shared_by_user',
        'expense',
        'expense__category',
        'income',
        'income__category',
    ).order_by('-created_at')
    return render(
        request,
        'sharing/group_detail.html',
        {
            'group': group,
            'members': members,
            'pending_members': pending_members,
            'transactions': transactions,
            'is_owner': group.owner_user_id == profile.user_id,
        },
    )


@login_required
def group_member_add(request, group_id):
    profile = _get_profile(request.user)
    group = get_object_or_404(SharingGroup, group_id=group_id, owner_user=profile)
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member_profile']
            if member.user_id == profile.user_id:
                form.add_error('member', 'Bạn đang là chủ nhóm nên không cần tự mời mình.')
            elif GroupMember.objects.filter(group=group, user=member, status=GroupMember.STATUS_ACTIVE).exists():
                form.add_error('member', 'Người này đang ở trong nhóm rồi.')
            else:
                _ensure_pending_member_status_supported()
                existing_membership = GroupMember.objects.filter(group=group, user=member).first()
                was_pending = existing_membership is not None and existing_membership.status == GroupMember.STATUS_PENDING
                membership, created = GroupMember.objects.update_or_create(
                    group=group,
                    user=member,
                    defaults={
                        'member_role': GroupMember.ROLE_MEMBER,
                        'status': GroupMember.STATUS_PENDING,
                        'joined_at': timezone.now(),
                    },
                )
                if was_pending:
                    messages.info(request, 'Lời mời đã được gửi trước đó, đang chờ người này xác nhận.')
                else:
                    if created:
                        messages.success(request, 'Đã gửi lời mời tham gia nhóm.')
                    else:
                        messages.success(request, 'Đã gửi lại lời mời tham gia nhóm.')
                return redirect('sharing_group_detail', group_id=group.group_id)
    else:
        form = AddMemberForm()
    return render(
        request,
        'sharing/member_form.html',
        {'form': form, 'group': group, 'page_title': 'Mời thành viên', 'submit_label': 'Gửi lời mời'},
    )


@login_required
@require_POST
def group_invitation_accept(request, membership_id):
    profile = _get_profile(request.user)
    membership = get_object_or_404(
        GroupMember.objects.select_related('group'),
        group_member_id=membership_id,
        user=profile,
        status=GroupMember.STATUS_PENDING,
    )
    membership.status = GroupMember.STATUS_ACTIVE
    membership.joined_at = timezone.now()
    membership.save(update_fields=['status', 'joined_at'])
    messages.success(request, f'Bạn đã tham gia nhóm {membership.group.group_name}.')
    return redirect('sharing_group_detail', group_id=membership.group_id)


@login_required
@require_POST
def group_invitation_decline(request, membership_id):
    profile = _get_profile(request.user)
    membership = get_object_or_404(
        GroupMember.objects.select_related('group'),
        group_member_id=membership_id,
        user=profile,
        status=GroupMember.STATUS_PENDING,
    )
    group_name = membership.group.group_name
    membership.status = GroupMember.STATUS_REMOVED
    membership.save(update_fields=['status'])
    messages.info(request, f'Bạn đã từ chối lời mời vào nhóm {group_name}.')
    return redirect('sharing_group_list')


@login_required
@require_POST
def group_toggle_status(request, group_id):
    profile = _get_profile(request.user)
    group = get_object_or_404(SharingGroup, group_id=group_id, owner_user=profile)

    if group.status == SharingGroup.STATUS_ARCHIVED:
        message = 'Nhóm đã lưu trữ nên không thể bật/tắt nhanh.'
        if _wants_json(request):
            return JsonResponse(
                {
                    'ok': False,
                    'is_on': False,
                    'label': group.get_status_display(),
                    'message': message,
                },
                status=400,
            )
        messages.info(request, message)
    elif group.status == SharingGroup.STATUS_ACTIVE:
        group.status = SharingGroup.STATUS_INACTIVE
        group.save(update_fields=['status', 'updated_at'])
        message = 'Đã tạm tắt nhóm.'
    else:
        group.status = SharingGroup.STATUS_ACTIVE
        group.save(update_fields=['status', 'updated_at'])
        message = 'Đã bật lại nhóm.'

    if _wants_json(request):
        return JsonResponse(
            {
                'ok': True,
                'is_on': group.status == SharingGroup.STATUS_ACTIVE,
                'label': group.get_status_display(),
                'message': message,
            }
        )

    messages.success(request, message)

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('sharing_group_list')


@login_required
def shared_transaction_create(request, group_id):
    profile = _get_profile(request.user)
    group = _member_group(profile, group_id)
    if request.method == 'POST':
        form = SharedTransactionForm(request.POST, user_profile=profile)
        if form.is_valid():
            shared = form.save(commit=False)
            shared.group = group
            shared.shared_by_user = profile
            shared.save()
            messages.success(request, 'Đã chia sẻ giao dịch vào nhóm.')
            return redirect('sharing_group_detail', group_id=group.group_id)
    else:
        form = SharedTransactionForm(user_profile=profile)
    return render(request, 'sharing/shared_transaction_form.html', {'form': form, 'group': group, 'page_title': 'Chia sẻ giao dịch', 'submit_label': 'Chia sẻ'})
