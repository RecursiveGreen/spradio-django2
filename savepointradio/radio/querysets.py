from datetime import timedelta

from django.db import models
from django.utils import timezone


class EnabledQuerySet(models.QuerySet):
    """
    Queryset to select all objects that are not disabled.
    """
    def enabled(self):
        return self.filter(disabled=False)


class PublishedQuerySet(models.QuerySet):
    """
    Queryset to select all objects that have been published.
    """
    def published(self):
        results = self.filter(
                       models.Q(published_date__isnull=False) &
                       models.Q(published_date__lte=timezone.now())
                  )
        return results


class TypeQuerySet(models.QuerySet):
    """
    Queryset to select all objects that are either songs or jingles.
    """
    def songs(self):
        return self.filter(song_type='S')

    def jingles(self):
        return self.filter(song_type='J')


class SongQuerySet(EnabledQuerySet,
                   PublishedQuerySet,
                   TypeQuerySet):
    """
    Queryset combination that can easily select enabled objects, published
    objects, and objects of a certain song type.
    """
    pass
