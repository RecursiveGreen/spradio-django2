from datetime import timedelta
from decimal import *
from random import randint

from django.db import models
from django.utils import timezone


# Set decimal precision
getcontext().prec = 16


def get_wait_until_next_play(song):
    """
    Length of time in seconds before a song can be played again.
    """
    if not song.last_played:
        return Decimal('0.00')

    wait = song.music.wait_total()
    nextplay = song.last_played + timedelta(seconds=float(wait))
    current = (nextplay - timezone.now()).total_seconds()

    return Decimal(current if current > 0 else 0).quantize(Decimal('.01'),
                                                           rounding=ROUND_UP)
