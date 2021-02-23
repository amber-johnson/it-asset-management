from django.contrib.auth.models import User

from equipment.models import *
from network.models import *
from power.models import *


def username(user):
    return user.username if user.is_authenticated else "_anonymous"


def display_name(user):
    return "Admin" if user.username == 'admin' else \
        user.first_name + " " + user.last_name


class ActionLog(models.Model):

    MODELS = {
        'Site': Site,
        'ITModel': ITModel,
        'Rack': Rack,
        'PDU': PDU,
        'Asset': Asset,
        'NetworkPortLabel': NetworkPortLabel,
        'NetworkPort': NetworkPort,
        'Powered': Powered,
    }

    class Action(models.TextChoices):
        CREATE = 'Create', 'Create'
        UPDATE = 'Update', 'Update'
        DESTROY = 'Destroy', 'Destroy'
        DECOMMISSION = 'Decommission', 'Decommission'

    action = models.CharField(
        choices=Action.choices,
        max_length=16
    )
    username = models.CharField(
        max_length=150
    )
    display_name = models.CharField(
        max_length=185
    )
    model = models.CharField(
        max_length=128
    )
    instance_id = models.IntegerField()
    identifier = models.CharField(
        blank=True,
        max_length=128
    )
    field_changed = models.CharField(
        blank=True,
        max_length=64
    )
    old_value = models.CharField(
        blank=True,
        max_length=8192
    )
    new_value = models.CharField(
        blank=True,
        max_length=8192
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        self.identifier = self.MODELS[self.model].objects.get(id=self.instance_id).__str__()
        super(ActionLog, self).save(*args, **kwargs)
