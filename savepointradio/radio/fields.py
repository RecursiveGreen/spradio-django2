'''
Custom model fields for the Save Point Radio project.
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.validators import RadioIRIValidator

from .forms import RadioIRIFormField


class RadioIRIField(models.TextField):
    '''
    A custom URL model field that allows schemes that match those from
    Liquidsoap. This is necessary due to a bug in how Django currently
    handles custom URLFields:

    https://code.djangoproject.com/ticket/25594
    https://stackoverflow.com/questions/41756572/
    '''

    default_validators = [RadioIRIValidator()]
    description = _("Long IRI")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        # This is a limit for Internet Explorer URLs
        kwargs.setdefault('max_length', 2000)
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == 2000:
            del kwargs['max_length']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': RadioIRIFormField,
            **kwargs,
        })
