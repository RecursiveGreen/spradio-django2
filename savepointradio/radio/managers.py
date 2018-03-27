from datetime import timedelta
from decimal import *

from django.db import models
from django.utils import timezone

from core.utils import get_setting
from .querysets import SongQuerySet


# Set decimal precision
getcontext().prec = 16


class SongManager(models.Manager):
    """
    Custom object manager for filtering out common behaviors for a playlist.
    """
    def get_queryset(self):
        return SongQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().songs().enabled().published()

    def playlist_length(self):
        """
        Total length of available songs in the playlist (in seconds).
        """
        return self.available().aggregate(models.Sum('length'))['length__sum']

    def wait_total(self):
        """
        Default length in seconds before a song can be played again. This is
        based on the replay ratio set in the application settings.
        """
        wait = self.playlist_length() * Decimal(get_setting('replay_ratio'))
        return wait.quantize(Decimal('.01'), rounding=ROUND_UP)

    def datetime_from_wait(self):
        """
        Datetime of now minus the default wait time for played songs.
        """
        return timezone.now() - timedelta(seconds=float(self.wait_total()))

    def playable(self):
        return self.available().filter(
                   models.Q(last_played__lt=self.datetime_from_wait()) |
                   models.Q(last_played__isnull=True)
               )
