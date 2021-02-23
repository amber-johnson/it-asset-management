from django.apps import AppConfig


class PowerConfig(AppConfig):
    name = 'power'

    def ready(self):
        from . import signals