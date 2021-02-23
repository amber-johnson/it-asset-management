from django.apps import AppConfig


class HyposoftConf(AppConfig):
    name = 'hyposoft'

    def ready(self):
        from . import signals
