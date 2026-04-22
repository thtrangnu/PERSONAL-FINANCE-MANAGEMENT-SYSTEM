from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from apps.accounts.services import sync_profile_for_user


@receiver(user_logged_in)
def sync_user_profile(sender, request, user, **kwargs):
    sync_profile_for_user(user)
