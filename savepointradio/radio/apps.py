from django.apps import AppConfig


class RadioConfig(AppConfig):
    name = 'radio'

    def ready(self):
        from .signals import cascade_disable, update_sorted_fields
