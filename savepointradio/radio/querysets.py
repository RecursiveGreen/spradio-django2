from django.db import models

from core.querysets import EnabledQuerySet, PublishedQuerySet


class SongTypeQuerySet(models.QuerySet):
    """
    Queryset to select all objects that are either songs or jingles.
    """
    def songs(self):
        return self.filter(song_type='S')

    def jingles(self):
        return self.filter(song_type='J')


class RadioQuerySet(EnabledQuerySet, PublishedQuerySet):
    """
    Queryset combination that can easily select enabled and published
    objects.
    """
    pass


class SongQuerySet(RadioQuerySet, SongTypeQuerySet):
    """
    Queryset combination that can easily select enabled objects, published
    objects, and objects of a certain song type.
    """
    pass
