'''
Custom Django model/form field validators for the Save Point Radio project.
'''

import re

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


GROUP_NT_UNC = r'file://[A-Za-z0-9!@#$%^&\'\)\(\.\-_{}~]+/'

GROUP_NT_DRIVE_LETTER = r'file:///[A-Za-z](?:\:|\|)/'

GROUP_NON_AUTH = r'file:///[A-Za-z0-9!@#$%^&\'\)\(\.\-_{}~]+'

FILE_IRI_PATTERN = (
    r'^(?P<unc>' +
    GROUP_NT_UNC +
    r')|(?P<driveletter>' +
    GROUP_NT_DRIVE_LETTER +
    r')|(?P<nonauth>' +
    GROUP_NON_AUTH +
    r')'
)


class RadioIRIValidator(validators.URLValidator):
    '''
    Validates an RFC3987-defined IRI along with RFC8089 for file:// and other
    custom schemes.
    '''

    message = _('Enter a valid IRI.')
    schemes = ['http', 'https', 'file', 'ftp', 'ftps', 's3']

    def __init__(self, schemes=None, **kwargs):
        super().__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def __call__(self, value):
        # Check the schemes first
        scheme = value.split('://')[0].lower()
        if scheme not in self.schemes:
            raise ValidationError(self.message, code=self.code)

        # Ignore the non-standard IRI
        if scheme == 'file':
            pattern = re.compile(FILE_IRI_PATTERN)
            if not pattern.match(value):
                raise ValidationError(self.message, code=self.code)
        elif scheme == 's3':
            # Nothing to validate, really. . .
            return
        else:
            super().__call__(value)
