'''
Various utlity functions that are independant of any Django app or
model.
'''

from nturl2path import pathname2url as ntpathname2url
from nturl2path import url2pathname as url2ntpathname
import random
import re
import string
from unicodedata import normalize
from urllib.parse import urljoin, urlparse
from urllib.request import pathname2url, url2pathname

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.utils.encoding import iri_to_uri, uri_to_iri

from .models import Setting
from .validators import GROUP_NT_DRIVE_LETTER, GROUP_NT_UNC


def generate_password(length=32):
    '''
    Quick and dirty random password generator.

    ***WARNING*** - Although this is likely "good enough" to create a secure
    password, there are no validations (suitible entropy, dictionary words,
    etc.) and should not be completely trusted. YOU HAVE BEEN WARNED.
    '''
    chars = string.ascii_letters + string.digits + string.punctuation
    rng = random.SystemRandom()
    return ''.join([rng.choice(chars) for i in range(length)])


def get_len(rawqueryset):
    '''
    Adds/Overrides a dynamic implementation of the length protocol to the
    definition of RawQuerySet.
    '''
    def __len__(self):
        params = ['{}'.format(p) for p in self.params]
        sql = ''.join(('SELECT COUNT(*) FROM (',
                       rawqueryset.raw_query.format(tuple(params)),
                       ') B;'))
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]
    return __len__


def get_setting(name):
    '''Helper function to get dynamic settings from the database.'''
    setting = Setting.objects.get(name=name)
    return setting.get()


def set_setting(name, value, setting_type=None):
    '''Helper function to set dynamic settings from the database.'''
    setting_types = {'Integer': 0, 'Float': 1, 'String': 2, 'Bool': 3}
    try:
        setting = Setting.objects.get(name=name)
        setting.data = str(value)
        if setting_type in setting_types:
            setting.setting_type = setting_types[setting_type]
        setting.save()
    except ObjectDoesNotExist:
        if setting_type in setting_types:
            Setting.objects.create(name=name,
                                   setting_type=setting_types[setting_type],
                                   data=str(value))
        else:
            error_msg = 'New settings need type (Integer, Float, String, Bool)'
            raise TypeError(error_msg)
    return


def naturalize(text):
    '''
    Return a normalized unicode string, with removed starting articles, for use
    in natural sorting.

    Code was inspired by 'django-naturalsortfield' from Nathan Reynolds:
    https://github.com/nathforge/django-naturalsortfield
    '''
    def naturalize_int_match(match):
        return '{:08d}'.format(int(match.group(0)))

    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    punc = re.compile('[{}]'.format(re.escape(string.punctuation)))
    text = re.sub(punc, ' ', text)
    text = text.strip()
    text = re.sub(r'^(a|an|the)\s+', '', text)
    text = re.sub(r'\d+', naturalize_int_match, text)

    return text


def quantify(quantity, model):
    '''
    A message based on the quantity and singular/plural name of the model.
    '''
    if quantity == 1:
        message = '1 {}'.format(model._meta.verbose_name)
    else:
        message = '{} {}'.format(str(quantity),
                                 model._meta.verbose_name_plural)
    return message


def create_success_message(parent_model, parent_quantity, child_model,
                           child_quantity, remove=False):
    '''
    Creates a message for displaying the success of model modification.
    '''
    p_message = quantify(parent_quantity, parent_model)
    c_message = quantify(child_quantity, child_model)
    if remove:
        return '{} successfully removed from {}'.format(c_message, p_message)
    return '{} successfully added to {}.'.format(c_message, p_message)


def get_pretty_time(seconds):
    '''
    Displays a human-readable representation of time.
    '''
    if seconds > 0:
        periods = [
            ('year', 60*60*24*365.25),
            ('day', 60*60*24),
            ('hour', 60*60),
            ('minute', 60),
            ('second', 1)
        ]
        strings = []
        for period_name, period_seconds in periods:
            if seconds >= period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                strings.append('{} {}{}'.format(period_value,
                                                period_name,
                                                ('s', '')[period_value == 1]))
        return ', '.join(strings)
    return 'Now'


def path_to_iri(path):
    '''
    OS-independant attempt at converting any OS absolute path to an
    RFC3987-defined IRI along with the file scheme from RFC8089.
    '''
    # Looking to see if the path starts with a drive letter or UNC path
    # (eg. 'D:\' or '\\')
    windows = re.match(r'^(?:[A-Za-z]:|\\)\\', path)
    if windows:
        return uri_to_iri(urljoin('file:', ntpathname2url(path)))
    return uri_to_iri(urljoin('file:', pathname2url(path)))


def iri_to_path(iri):
    '''
    OS-independant attempt at converting an RFC3987-defined IRI with a file
    scheme from RFC8089 to an OS-specific absolute path.
    '''
    # Drive letter IRI will have three slashes followed by the drive letter
    # UNC path IRI will have two slashes followed by the UNC path
    uri = iri_to_uri(iri)
    patt = r'^(?:' + GROUP_NT_DRIVE_LETTER + r'|' + GROUP_NT_UNC + r')'
    windows = re.match(patt, uri)
    if windows:
        parse = urlparse(uri)
        # UNC path URIs put the server name in the 'netloc' parameter.
        if parse.netloc:
            return '\\' + url2ntpathname('/' + parse.netloc + parse.path)
        return url2ntpathname(parse.path)
    return url2pathname(urlparse(uri).path)
