from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.behaviors import Timestampable
from .behaviors import Disableable, Publishable
from .managers import SongManager


class Album(Disableable, Publishable, Timestampable, models.Model):
    """
    A model for a music album.
    """
    title = models.CharField(_('title'), max_length=255, unique=True)

    def __str__(self):
        return self.title


class Artist(Disableable, Publishable, Timestampable, models.Model):
    """
    A model for a music artist.
    """
    alias = models.CharField(_('alias'), max_length=127, blank=True)
    first_name = models.CharField(_('first name'), max_length=127, blank=True)
    last_name = models.CharField(_('last name'), max_length=127, blank=True)

    class Meta:
        ordering = ('first_name', 'alias',)

    @property
    def full_name(self):
        if not self.alias:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            if not self.first_name or not self.last_name:
                return self.alias
            else:
                return '{} "{}" {}'.format(self.first_name,
                                           self.alias,
                                           self.last_name)

    def __str__(self):
        return self.full_name


class Game(Disableable, Publishable, Timestampable, models.Model):
    """
    A model for a game.
    """
    title = models.CharField(_('title'), max_length=255, unique=True)

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

    objects = models.Manager()
    music = SongManager()

    def __str__(self):
        if self.song_type == 'J':
            return self.title
        else:
            all_artists = ', '.join([a.full_name for a in self.artists.all()])
            return '{} - {} ({})'.format(self.game.title,
                                         self.title,
                                         all_artists)
