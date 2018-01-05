import re
from unicodedata import normalize

from django.db import models


class NaturalSortField(models.CharField):
    """
    A custom model field specifically for storing a normalized unicode string,
    with removed starting articles, for use in natural sorting.

    Code is a modified version of 'django-naturalsortfield' by Nathan Reynolds:
    https://github.com/nathforge/django-naturalsortfield
    """
    def __init__(self, for_field, **kwargs):
        self.for_field = for_field
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('max_length', 255)
        super(NaturalSortField, self).__init__(**kwargs)

    def pre_save(self, model_instance, add):
        return self.naturalize(getattr(model_instance, self.for_field))

    def naturalize(self, string):
        def naturalize_int_match(match):
            return '%08d' % (int(match.group(0)),)

        string = normalize('NFKD', string).encode('ascii', 'ignore').decode('ascii')
        string = string.lower()
        string = string.strip()
        string = re.sub(r'^(a|an|the)\s+', '', string)
        string = re.sub(r'\d+', naturalize_int_match, string)

        return string
