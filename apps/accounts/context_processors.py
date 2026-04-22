from django.db import DatabaseError

from apps.accounts.models import UserProfile
from apps.alerts.models import Alert
from apps.sharing.models import GroupMember


def navigation_profile(request):
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {
            'nav_profile': None,
            'nav_avatar_url': '',
            'nav_display_name': '',
            'nav_alerts': [],
            'nav_group_invitations': [],
            'nav_unread_alert_count': 0,
        }

    profile = None
    try:
        profile = UserProfile.objects.filter(username=user.username).first()
        if profile is None and user.email:
            profile = UserProfile.objects.filter(email=user.email).first()
    except DatabaseError:
        profile = None

    display_name = ''
    avatar_url = ''
    nav_alerts = []
    nav_group_invitations = []
    unread_alert_count = 0
    if profile is not None:
        display_name = profile.full_name or profile.username
        avatar_url = profile.avatar_url or ''
        try:
            nav_alerts = list(
                Alert.objects.filter(user=profile)
                .select_related('related_budget', 'related_expense')
                .order_by('-created_at', '-alert_id')[:5]
            )
            unread_alert_count = Alert.objects.filter(user=profile, is_read=False).count()
            nav_group_invitations = list(
                GroupMember.objects.filter(user=profile, status=GroupMember.STATUS_PENDING)
                .select_related('group', 'group__owner_user')
                .order_by('-joined_at')[:3]
            )
        except DatabaseError:
            nav_alerts = []
            nav_group_invitations = []
            unread_alert_count = 0

    if not display_name:
        display_name = user.get_full_name() or user.username

    return {
        'nav_profile': profile,
        'nav_avatar_url': avatar_url,
        'nav_display_name': display_name,
        'nav_alerts': nav_alerts,
        'nav_group_invitations': nav_group_invitations,
        'nav_unread_alert_count': unread_alert_count + len(nav_group_invitations),
    }
