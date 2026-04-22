from apps.accounts.models import UserProfile


def sync_profile_for_user(user):
    """Keep the finance profile aligned with Django's auth user."""
    username = user.username
    email = user.email or f'{username}@example.local'
    full_name = user.get_full_name() or username

    profile = UserProfile.objects.filter(username=username).first()
    if profile is None:
        profile = UserProfile.objects.filter(email=email).first()

    if profile is None:
        return UserProfile.objects.create(
            username=username,
            email=email,
            password_hash=user.password,
            full_name=full_name,
            role=UserProfile.ROLE_ADMIN if user.is_staff else UserProfile.ROLE_USER,
            is_active=user.is_active,
            default_currency='VND',
        )

    username_is_available = not UserProfile.objects.exclude(pk=profile.pk).filter(username=username).exists()
    email_is_available = not UserProfile.objects.exclude(pk=profile.pk).filter(email=email).exists()

    if username_is_available:
        profile.username = username
    if email_is_available:
        profile.email = email

    profile.password_hash = user.password
    if full_name and (not profile.full_name or profile.full_name == profile.username):
        profile.full_name = full_name
    profile.role = UserProfile.ROLE_ADMIN if user.is_staff else UserProfile.ROLE_USER
    profile.is_active = user.is_active
    profile.default_currency = profile.default_currency or 'VND'
    profile.save()
    return profile

