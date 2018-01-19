from django.conf import settings
from django.core.validators import (MaxLengthValidator, MinValueValidator,
                                    MaxValueValidator)
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.behaviors import Timestampable
from radio.models import Song
from .managers import RequestManager


class RadioProfile(Timestampable, models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    favorites = models.ManyToManyField(Song, related_name='song_favorites')
    ratings = models.ManyToManyField(Song,
                                     related_name='song_ratings',
                                     through='Rating')
    song_requests = models.ManyToManyField(Song,
                                           related_name='song_requests',
                                           through='SongRequest')

    def __str__(self):
        return "{}'s profile".format(self.user.get_username())


class Rating(Timestampable, models.Model):
    profile = models.ForeignKey(RadioProfile,
                                on_delete=models.CASCADE,
                                related_name='rating_profile')
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    value = models.PositiveIntegerField(_('song rating'),
                                        validators=[MinValueValidator(1),
                                                    MaxValueValidator(5)])

    def __str__(self):
        return "{} - {}'s Rating: {}".format(self.song.title,
                                             self.profile.user.get_username(),
                                             self.value)


class SongRequest(Timestampable, models.Model):
    profile = models.ForeignKey(RadioProfile,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='request_profile')
    song = models.ForeignKey(Song,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)
    queued_at = models.DateTimeField(_('song queued at'),
                                     default=None,
                                     blank=True,
                                     null=True)
    played_at = models.DateTimeField(_('song played at'),
                                     default=None,
                                     blank=True,
                                     null=True)

    objects = models.Manager()
    music = RequestManager()

    class Meta:
        ordering = ['-created_date', ]

    def __str__(self):
        req_user = self.profile.user.get_username()
        return "{} - Requested by {} at {}".format(self.song.title,
                                                   req_user,
                                                   self.created_date)
