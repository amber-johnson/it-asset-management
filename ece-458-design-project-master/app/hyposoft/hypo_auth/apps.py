from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'hypo_auth'

    def ready(self):
        from . import signals
