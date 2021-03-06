'''
Django Models for the Radio application.
'''

from datetime import timedelta
from decimal import getcontext, Decimal, ROUND_UP

from django.apps import apps
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.behaviors import Disableable, Publishable, Timestampable
from core.utils import get_setting
from .fields import RadioIRIField
from .managers import RadioManager, SongManager


# Set decimal precision
getcontext().prec = 16


class Album(Disableable, Publishable, Timestampable, models.Model):
    '''
    A model for a music album.
    '''
    title = models.CharField(_('title'), max_length=255, unique=True)

    sorted_title = models.CharField(_('naturalized title'),
                                    db_index=True,
                                    editable=False,
                                    max_length=255)

    objects = models.Manager()
    music = RadioManager()

    class Meta:
        ordering = ['sorted_title', ]

    def __str__(self):
        return self.title


class Artist(Disableable, Publishable, Timestampable, models.Model):
    '''
    A model for a music artist.
    '''
    alias = models.CharField(_('alias'), max_length=127, blank=True)
    first_name = models.CharField(_('first name'), max_length=127, blank=True)
    last_name = models.CharField(_('last name'), max_length=127, blank=True)

    sorted_full_name = models.CharField(_('naturalized full name'),
                                        db_index=True,
                                        editable=False,
                                        max_length=255)

    objects = models.Manager()
    music = RadioManager()

    class Meta:
        ordering = ['sorted_full_name', ]

    @property
    def full_name(self):
        '''
        String representing the artist's full name including an alias, if
        available.
        '''
        if self.alias:
            if self.first_name or self.last_name:
                return '{} "{}" {}'.format(self.first_name,
                                           self.alias,
                                           self.last_name)
            return self.alias
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


class Game(Disableable, Publishable, Timestampable, models.Model):
    '''
    A model for a game.
    '''
    title = models.CharField(_('title'), max_length=255, unique=True)

    sorted_title = models.CharField(_('naturalized title'),
                                    db_index=True,
                                    editable=False,
                                    max_length=255)

    objects = models.Manager()
    music = RadioManager()

    class Meta:
        ordering = ['sorted_title', ]

    def __str__(self):
        return self.title


class Store(Timestampable, models.Model):
    '''
    A model to represent various data locations (stores) for the song.
    '''
    iri = RadioIRIField(_('IRI path to song file'))
    mime_type = models.CharField(_('file MIME type'),
                                 max_length=64,
                                 blank=True)
    file_size = models.BigIntegerField(_('file size'),
                                       validators=[MinValueValidator(0)],
                                       blank=True,
                                       null=True)
    length = models.DecimalField(_('song length (in seconds)'),
                                 max_digits=8,
                                 decimal_places=2,
                                 null=True,
                                 blank=True)
    track_gain = models.DecimalField(_('recommended replaygain adjustment'),
                                     max_digits=6,
                                     decimal_places=2,
                                     null=True,
                                     blank=True)
    track_peak = models.DecimalField(_('highest volume level in the track'),
                                     max_digits=10,
                                     decimal_places=6,
                                     null=True,
                                     blank=True)

    def _replaygain(self):
        '''
        String representation of the recommended amplitude adjustment.
        '''
        if self.track_gain is None:
            return '+0.00 dB'
        if self.track_gain > 0:
            return '+{} dB'.format(str(self.track_gain))
        return '{} dB'.format(str(self.track_gain))
    replaygain = property(_replaygain)

    def __str__(self):
        return self.iri


class Song(Disableable, Publishable, Timestampable, models.Model):
    '''
    A model for a song.
    '''
    JINGLE = 'J'
    SONG = 'S'
    TYPE_CHOICES = (
        (JINGLE, 'Jingle'),
        (SONG, 'Song'),
    )
    album = models.ForeignKey(Album,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    game = models.ForeignKey(Game,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True)
    song_type = models.CharField(_('song type'),
                                 max_length=1,
                                 choices=TYPE_CHOICES,
                                 default=SONG)
    title = models.CharField(_('title'), max_length=255)
    num_played = models.PositiveIntegerField(_('number of times played'),
                                             default=0)
    last_played = models.DateTimeField(_('was last played'),
                                       null=True,
                                       blank=True,
                                       editable=False)
    next_play = models.DateTimeField(_('can be played again'),
                                     null=True,
                                     blank=True,
                                     editable=False)
    stores = models.ManyToManyField(Store, blank=True, related_name='song')
    active_store = models.ForeignKey(Store,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True,
                                     related_name='active_for')
    sorted_title = models.CharField(_('naturalized title'),
                                    db_index=True,
                                    editable=False,
                                    max_length=255)

    objects = models.Manager()
    music = SongManager()

    class Meta:
        ordering = ['sorted_title', ]

    def _is_jingle(self):
        '''
        Is the object a jingle?
        '''
        return self.song_type == 'J'
    _is_jingle.boolean = True
    is_jingle = property(_is_jingle)

    def _is_song(self):
        '''
        Is the object a song?
        '''
        return self.song_type == 'S'
    _is_song.boolean = True
    is_song = property(_is_song)

    def _is_available(self):
        '''
        Is the object both enabled and published?
        '''
        return self._is_enabled() and self._is_published()
    _is_available.boolean = True
    is_available = property(_is_available)

    def _full_title(self):
        '''
        String representing the entire song title, including the game and
        artists involved.
        '''
        if self._is_song():
            enabled_artists = self.artists.all().filter(disabled=False)
            all_artists = ', '.join([a.full_name for a in enabled_artists])
            return '{} - {} [{}]'.format(self.game.title,
                                         self.title,
                                         all_artists)
        return self.title
    full_title = property(_full_title)

    def _average_rating(self):
        '''
        Decimal number of the average rating of a song from 1 - 5.
        '''
        ratings = self.rating_set.all()
        if ratings:
            avg = Decimal(ratings.aggregate(avg=models.Avg('value'))['avg'])
            return avg.quantize(Decimal('.01'), rounding=ROUND_UP)
        return None
    average_rating = property(_average_rating)

    def get_time_until_requestable(self):
        '''
        Length of time before a song can be requested again.
        '''
        if self._is_song() and self._is_available():
            if self.last_played:
                allowed_datetime = Song.music.datetime_from_wait()
                remaining_wait = self.last_played - allowed_datetime
                if remaining_wait.total_seconds() > 0:
                    return remaining_wait
            return timedelta(seconds=0)
        return None

    def get_date_when_requestable(self, last_play=None):
        '''
        Datetime when a song can be requested again.
        '''
        last = self.last_played if last_play is None else last_play

        if self._is_song() and self._is_available():
            if last:
                # Check if we have enough ratings to change ratio
                min_ratings = get_setting('min_ratings_for_variance')
                if self.rating_set.count() >= min_ratings:
                    rate_ratio = get_setting('rating_variance_ratio')

                    # -((average - 1)/(highest_rating - 1)) * rating_ratio
                    base = -((self._average_rating() - 1) / 4) * rate_ratio
                    adjusted_ratio = float(base + (rate_ratio * 0.5))
                else:
                    adjusted_ratio = float(0.0)

                return last + Song.music.wait_total(adjusted_ratio)
            return timezone.now()
        return None

    def _is_playable(self):
        '''
        Is the song available and not been played within the default waiting
        period (or at all)?
        '''
        if self._is_song() and self._is_available():
            return self.get_date_when_requestable() <= timezone.now()
        return False
    _is_playable.boolean = True
    is_playable = property(_is_playable)

    def _is_requestable(self):
        '''
        Is the song playable and has it not already been requested?
        '''
        if self._is_playable():
            song_request = apps.get_model(app_label='profiles',
                                          model_name='SongRequest')
            requests = song_request.music.unplayed().values_list('song__id',
                                                                 flat=True)
            return self.pk not in requests
        return False
    _is_requestable.boolean = True
    is_requestable = property(_is_requestable)

    def __str__(self):
        return self.title
