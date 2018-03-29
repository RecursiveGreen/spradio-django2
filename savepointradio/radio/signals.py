from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from core.utils import naturalize
from .models import Album, Artist, Game, Song


@receiver(pre_save, sender=Album)
@receiver(pre_save, sender=Artist)
@receiver(pre_save, sender=Game)
@receiver(pre_save, sender=Song)
def update_sorted_fields(sender, instance, **kwargs):
    """
    Whenever the name or title of a radio model object is created/modified, we
    want to make sure we update the sorted field with the naturalized data for
    sorting.
    """
    if sender == Artist:
        instance.sorted_full_name = naturalize(instance.full_name)
    else:
        instance.sorted_title = naturalize(instance.title)


@receiver(post_save, sender=Album)
@receiver(post_save, sender=Artist)
@receiver(post_save, sender=Game)
@receiver(post_save, sender=Song)
def cascade_disable(sender, instance, created, update_fields, **kwargs):
    """
    If a radio object is disabled, be sure to update other objects that are
    linked to it.
    """
    if 'disabled' in update_fields:
        if instance.disabled:
            time = timezone.now()
            if sender == Artist:
                title = instance.full_name
            else:
                title = instance.title
            reason = '{} "{}" was disabled.'.format(sender.__name__, title)
        else:
            time = None
            reason = ''

        # The multiple <model>_as_queryset's below are used to get around a
        # potential infinite loop from the signal. Using .update() does not
        # trigger it.

        # Disabling/Enabling an album does the same to all linked songs
        if sender == Album:
            album_songs = Song.objects.filter(album=instance)
            album_songs.update(disabled=instance.disabled,
                               disabled_date=time,
                               disabled_reason=reason)

        # Disabling/Enabling an artist will only affect songs in which they
        # are the only artist.
        if sender == Artist:
            for song in Song.objects.filter(artists=instance):
                if song.artists.count() == 1:
                    song_as_queryset = Song.objects.filter(pk=song.pk)
                    song_as_queryset.update(disabled=instance.disabled,
                                            disabled_date=time,
                                            disabled_reason=reason)

        # Disabling/Enabling an game does the same to all linked songs
        if sender == Game:
            game_songs = Song.objects.filter(game=instance)
            game_songs.update(disabled=instance.disabled,
                              disabled_date=time,
                              disabled_reason=reason)

        # Disabling a song does nothing, but enabling a song will enable all
        # linked albums, artists, and games.
        if sender == Song:
            if not instance.disabled:
                album_as_queryset = Album.objects.filter(pk=instance.album.pk)
                album_as_queryset.update(disabled=instance.disabled,
                                         disabled_date=time,
                                         disabled_reason=reason)

                instance.artists.all().update(disabled=instance.disabled,
                                              disabled_date=time,
                                              disabled_reason=reason)

                game_as_queryset = Album.objects.filter(pk=instance.game.pk)
                game_as_queryset.update(disabled=instance.disabled,
                                        disabled_date=time,
                                        disabled_reason=reason)
