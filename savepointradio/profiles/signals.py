from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RadioProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile object after a new user is created and link them.
    """
    if created:
        profile, new = RadioProfile.objects.get_or_create(user=instance)
