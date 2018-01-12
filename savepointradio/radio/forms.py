from django.forms import inlineformset_factory

from .models import Song


ArtistFormSet = inlineformset_factory(Song,
                                      Song.artists.through,
                                      fields=('artist',),
                                      can_delete=False,
                                      extra=10,)
