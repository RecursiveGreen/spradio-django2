from django.db import models

from .querysets import SongQuerySet


class SongManager(models.Manager):
    """
    Custom object manager for filtering out common behaviors for a playlist.
    """
    def get_queryset(self):
        return SongQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().songs().enabled().published()
