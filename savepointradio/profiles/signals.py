from django.conf import settings
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RadioProfile, SongRequest


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile object after a new user is created and link them.
    """
    if created:
        profile, new = RadioProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=SongRequest)
def update_song_plays(sender, instance, created, update_fields, **kwargs):
    """
    Set when a song can be requested again once it's queued. Once played,
    update the song data with the latest play time and the number of times
    played.
    """
    if not created and update_fields:
        song = instance.song
        if 'played_at' in update_fields:
            song.last_played = instance.played_at
            song.num_played = F('num_played') + 1
            song.save()
        if 'queued_at' in update_fields:
            if song.is_song:
                queued = instance.queued_at
                song.next_play = song.get_date_when_requestable(queued)
                song.save()
