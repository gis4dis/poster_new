from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.dispatch import receiver


# noinspection PyUnusedLocal
@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):

    user.is_active = False
    user.is_staff = False
    user.save()
