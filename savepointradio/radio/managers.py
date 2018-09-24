from datetime import timedelta
from decimal import getcontext, Decimal, ROUND_UP
from random import randint

from django.apps import apps
from django.db import models
from django.utils import timezone

from core.utils import get_setting
from .querysets import RadioQuerySet, SongQuerySet


# Set decimal precision
getcontext().prec = 16


class RadioManager(models.Manager):
    """
    Custom object manager for filtering out common behaviors for radio
    objects.
    """
    def get_queryset(self):
        """
        Return customized default QuerySet.
        """
        return RadioQuerySet(self.model, using=self._db)

    def disabled(self):
        """
        Radio objects that are marked as disabled.
        """
        return self.get_queryset().disabled()

    def enabled(self):
        """
        Radio objects that are marked as enabled.
        """
        return self.get_queryset().enabled()

    def published(self):
        """
        Radio objects that are marked as published.
        """
        return self.get_queryset().published()

    def unpublished(self):
        """
        Radio objects that are marked as unpublished.
        """
        return self.get_queryset().unpublished()

    def available(self):
        """
        Radio objects that are enabled and published.
        """
        return self.enabled().published()


class SongManager(RadioManager):
    """
    Custom object manager for filtering out common behaviors for Song objects.
    """
    def get_queryset(self):
        """
        Return customized default QuerySet for Songs.
        """
        return SongQuerySet(self.model, using=self._db)

    def available_jingles(self):
        """
        Jingles that are currently published and are enabled.
        """
        return self.available().jingles()

    def available_songs(self):
        """
        Songs that are currently published and are enabled.
        """
        return self.available().songs()

    def playlist_length(self):
        """
        Total length of available songs in the playlist (in seconds).
        """
        length = self.available_songs().aggregate(models.Sum('length'))
        return length['length__sum']

    def wait_total(self):
        """
        Default length in seconds before a song can be played again. This is
        based on the replay ratio set in the application settings.
        """
        wait = self.playlist_length() * Decimal(get_setting('replay_ratio'))
        wait = wait.quantize(Decimal('.01'), rounding=ROUND_UP)
        return timedelta(seconds=float(wait))

    def datetime_from_wait(self):
        """
        Datetime of now minus the default wait time for played songs.
        """
        return timezone.now() - self.wait_total()

    def playable(self):
        """
        Songs that are playable because they are available (enabled &
        published) and they have not been played within the default wait time
        (or at all).
        """
        return self.available_songs().filter(
                    models.Q(last_played__lt=self.datetime_from_wait()) |
                    models.Q(last_played__isnull=True)
               )

    def requestable(self):
        """
        Songs that can be placed in the request queue for playback.
        """
        # Import SongRequest here to get rid of circular dependencies
        SongRequest = apps.get_model(app_label='profiles',
                                     model_name='SongRequest')
        requests = SongRequest.music.unplayed().values_list('song__id',
                                                            flat=True)
        return self.playable().exclude(id__in=requests)

    def get_random_requestable_song(self):
        """
        Pick a random requestable song and return it.
        """
        return self.requestable()[randint(0, self.requestable().count() - 1)]

    def get_random_jingle(self):
        """
        Pick a random jingle and return it.
        """
        random_index = randint(0, self.available_jingles().count() - 1)
        return self.available_jingles()[random_index]
