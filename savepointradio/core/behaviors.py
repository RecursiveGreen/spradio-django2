from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Timestampable(models.Model):
    created_date = models.DateTimeField(_('added on'), auto_now_add=True)
    modified_date = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        abstract = True
