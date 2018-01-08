from django.db.models.signals import pre_save
from django.dispatch import receiver

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
