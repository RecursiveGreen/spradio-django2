from django.conf import settings
from django.core.validators import (MaxLengthValidator, MinValueValidator,
                                    MaxValueValidator)
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.behaviors import Disableable, Timestampable
from core.utils import get_setting
from radio.models import Song
from .exceptions import MakeRequestError
from .managers import RequestManager


class RadioProfile(Disableable, Timestampable, models.Model):
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

    def disable(self, reason=''):
        super().disable(reason)
        user = self.user
        user.is_active = False
        user.save(update_fields=['is_active'])

    def enable(self):
        super().enable()
        user = self.user
        user.is_active = True
        user.save(update_fields=['is_active'])

    def has_reached_request_max(self):
        self_requests = SongRequest.music.unplayed().filter(profile=self)
        max_requests = get_setting('max_song_requests')
        return self_requests.count() >= max_requests

    def can_request(self):
        if not self.disabled:
            return self.user.is_staff or not self.has_reached_request_max()
        return False

    def make_request(self, song_requested):
        if isinstance(song_requested, int):
            song = Song.objects.get(pk=song_requested)
        else:
            song = song_requested

        if self.disabled:
            raise MakeRequestError('User is currently disabled.')

        if self.has_reached_request_max():
            max_requests = get_setting('max_song_requests')
            message = 'User has reached the maximum request limit ({}).'
            raise MakeRequestError(message.format(max_requests))

        if song.is_jingle and not self.user.is_staff:
            raise MakeRequestError('Users cannot request a jingle.')

        if song.is_song and not self.user.is_staff and not song.is_requestable:
            if not song.is_available:
                raise MakeRequestError('Song not available at this time.')

            if song.is_playable:
                raise MakeRequestError('Song is already in request queue.')

            play_again = song.get_date_when_requestable().isoformat(' ',
                                                                    'seconds')
            message = ('Song has been played recently and cannot be requested '
                       'again until {}')
            raise MakeRequestError(message.format(play_again))

        SongRequest.objects.create(profile=self, song=song)

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
