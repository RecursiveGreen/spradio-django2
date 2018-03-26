import random
import re
import string
from unicodedata import normalize

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from .models import Setting


def generate_password(length=32):
    chars = string.ascii_letters + string.digits + string.punctuation
    rng = random.SystemRandom()
    return ''.join([rng.choice(chars) for i in range(length)])


def get_len(rawqueryset):
    """
    Adds/Overrides a dynamic implementation of the length protocol to the
    definition of RawQuerySet.
    """
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
    setting = Setting.objects.get(name=name)
    return setting.get()


def set_setting(name, value, setting_type=None):
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
    """
    Return a normalized unicode string, with removed starting articles, for use
    in natural sorting.

    Code was inspired by 'django-naturalsortfield' from Nathan Reynolds:
    https://github.com/nathforge/django-naturalsortfield
    """
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
    """
    A message based on the quantity and singular/plural name of the model.
    """
    if quantity == 1:
        message = '1 {}'.format(model._meta.verbose_name)
    else:
        message = '{} {}'.format(str(quantity),
                                 model._meta.verbose_name_plural)
    return message


def create_success_message(parent_model, parent_quantity, child_model,
                           child_quantity, remove=False):
    """
    Creates a message for displaying the success of model modification.
    """
    p_message = quantify(parent_quantity, parent_model)
    c_message = quantify(child_quantity, child_model)
    if remove:
        return '{} successfully removed from {}'.format(c_message, p_message)
    else:
        return '{} successfully added to {}.'.format(c_message, p_message)


def get_pretty_time(seconds):
    """
    Displays a human-readable representation of time.
    """
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
    else:
        return 'Now'
