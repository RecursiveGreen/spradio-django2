import random
import string

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from .models import Setting


def generate_password(length=32):
    possible_characters = string.ascii_letters + string.digits + string.punctuation
    rng = random.SystemRandom()
    return ''.join([rng.choice(possible_characters) for i in range(length)])

def get_len(rawqueryset):
    """
    Adds/Overrides a dynamic implementation of the length protocol to the
    definition of RawQuerySet.
    """
    def __len__(self):
        params = ['{}'.format(p) for p in self.params]
        sql = 'SELECT COUNT(*) FROM (' + rawqueryset.raw_query.format(tuple(params)) + ') B;'
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
            error_msg = 'New settings need a type (Integer, Float, String, Bool)'
            raise TypeError(error_msg)
    return