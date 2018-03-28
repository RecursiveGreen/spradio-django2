from datetime import timedelta
from decimal import getcontext, Decimal, ROUND_UP

from django.apps import apps
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
        """
        Return customized default QuerySet for Songs.
        """
        return SongQuerySet(self.model, using=self._db)

    def available(self):
        """
        Songs that are currently published and are enabled.
        """
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
        return self.available().filter(
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
