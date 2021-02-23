from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    name = 'equipment'

    def ready(self):
        from . import signals
