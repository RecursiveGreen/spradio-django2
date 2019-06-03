'''
Custom forms/formfields for the Save Point Radio project.
'''

from django.core import validators
from django.forms.fields import URLField


ALLOWED_SCHEMES = ['http', 'https', 'file', 'ftp', 'ftps', 's3']


class RadioIRIFormField(URLField):
    '''
    A custom URL form field that allows schemes that match those from
    Liquidsoap. This is necessary due to a bug in how Django currently
    handles custom URLFields:

    https://code.djangoproject.com/ticket/25594
    https://stackoverflow.com/questions/41756572/
    '''
    default_validators = [validators.URLValidator(schemes=ALLOWED_SCHEMES)]
