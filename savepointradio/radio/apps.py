from django.apps import AppConfig


class RadioConfig(AppConfig):
    name = 'radio'

    def ready(self):
        from .signals import update_sorted_fields
