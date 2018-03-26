from datetime import timedelta
from decimal import *
from random import randint

from django.db import models
from django.utils import timezone

from core.utils import get_setting
from .models import Song


# Set decimal precision
getcontext().prec = 16


def get_playlist_length():
    """
    Total length of available songs in the playlist (in seconds).
    """
    songs = Song.music.available()
    return songs.aggregate(models.Sum('length'))['length__sum']


def get_waittime():
    """
    Default length in seconds before a song can be played again. This is based
    on the replay ratio set in the application settings.
    """
    waittime = get_playlist_length() * Decimal(get_setting('replay_ratio'))
    return waittime.quantize(Decimal('.01'), rounding=ROUND_UP)


def get_next_allowed_play_time(song):
    """
    Length of time in seconds before a song can be played again.
    """
    if not song.last_played:
        return Decimal('0.00')

    waittime = get_waittime()
    nextplay = song.last_played + timedelta(seconds=float(waittime))
    current = (nextplay - timezone.now()).total_seconds()

    return Decimal(current if current > 0 else 0).quantize(Decimal('.01'),
                                                           rounding=ROUND_UP)
