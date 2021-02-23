from django.apps import AppConfig


class ChangeplanConfig(AppConfig):
    name = 'changeplan'

    def ready(self):
        from . import signals