# web/signals.py

from allauth.account.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def promote_middlebury_users_to_staff(request, user, **kwargs):
    """Make @middlebury.edu users staff automatically after login."""
    if user.email and user.email.endswith('@middlebury.edu'):
        if not user.is_staff:
            user.is_staff = True
            user.save()