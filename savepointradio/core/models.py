from django.db import models
from django.utils.translation import ugettext_lazy as _

from authtools.models import AbstractNamedUser


class RadioUser(AbstractNamedUser):
    """
    Custom user model which uses email as the main identifier and adds a flag
    for whether the user is the radio DJ.
    """
    is_dj = models.BooleanField(_('dj status'),
                                default=False,
                                help_text=_('Designates whether this user is '
                                            'the automated dj account or is a '
                                            'real person account.'))


class Setting(models.Model):
    """
    A model for keeping track of dynamic settings while the site is online and
    the radio is running.
    """
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    BOOL = 3
    TYPE_CHOICES = (
        (INTEGER, 'Integer'),
        (FLOAT, 'Float'),
        (STRING, 'String'),
        (BOOL, 'Bool'),
    )
    name = models.CharField(_('name'), max_length=64, unique=True)
    description = models.TextField(_('description'), blank=True)
    setting_type = models.PositiveIntegerField(_('variable type'),
                                               choices=TYPE_CHOICES,
                                               default=INTEGER)
    data = models.TextField(_('data'))

    def get(self):
        if self.setting_type == self.INTEGER:
            return int(self.data)
        elif self.setting_type == self.FLOAT:
            return float(self.data)
        elif self.setting_type == self.BOOL:
            return self.data == 'True'
        else:
            return self.data

    def __str__(self):
        return '{}: {}'.format(self.name, self.data)
