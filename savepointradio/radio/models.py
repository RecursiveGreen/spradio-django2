from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.behaviors import Disableable, Publishable, Timestampable
from .managers import RadioManager, SongManager


class Album(Disableable, Publishable, Timestampable, models.Model):
    """
    A model for a music album.
    """
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
    """
    A model for a music artist.
    """
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
        """
        String representing the artist's full name including an alias, if
        available.
        """
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
    """
    A model for a game.
    """
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


class Song(Disableable, Publishable, Timestampable, models.Model):
    """
    A model for a song.
    """
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
    artists = models.ManyToManyField(Artist)
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
    length = models.DecimalField(_('song length (in seconds)'),
                                 max_digits=8,
                                 decimal_places=2,
                                 null=True,
                                 blank=True)
    path = models.TextField(_('absolute path to song file'))

    sorted_title = models.CharField(_('naturalized title'),
                                    db_index=True,
                                    editable=False,
                                    max_length=255)

    objects = models.Manager()
    music = SongManager()

    class Meta:
        ordering = ['sorted_title', ]

    @property
    def full_title(self):
        """
        String representing the entire song title, including the game and
        artists involved.
        """
        if self.song_type == 'S':
            all_artists = ', '.join([a.full_name for a in self.artists.all()])
            return '{} - {} [{}]'.format(self.game.title,
                                         self.title,
                                         all_artists)
        return self.title

    def get_time_until_requestable(self):
        """
        Length of time before a song can be requested again.
        """
        if self.song_type == 'S':
            if self.last_played:
                allowed_datetime = Song.music.datetime_from_wait()
                remaining_wait = self.last_played - allowed_datetime
                if remaining_wait.total_seconds() > 0:
                    return remaining_wait
                return timedelta(seconds=0)
            return timedelta(seconds=0)
        return None

    def get_date_when_requestable(self):
        """
        Datetime when a song can be requested again.
        """
        if self.song_type == 'S':
            return self.last_played + Song.music.wait_total()
        return None

    def _is_requestable(self):
        """
        Can the song be requested or not?
        """
        if self.song_type == 'S':
            return self.get_date_when_requestable() <= timezone.now()
        return False
    _is_requestable.boolean = True
    is_requestable = property(_is_requestable)

    def __str__(self):
        return self.title
