from django.core.validators import RegexValidator
from django.db import models
from equipment.models import ITModel, Asset
from changeplan.models import ChangePlan


class NetworkPortLabel(models.Model):
    name = models.CharField(
        max_length=16,
        blank=True
    )
    itmodel = models.ForeignKey(
        ITModel,
        on_delete=models.CASCADE
    )
    order = models.IntegerField()

    class Meta:
        unique_together = [['name', 'itmodel'], ['itmodel', 'order']]

    def __str__(self):
        return '{} : {}'.format(self.name, self.itmodel)


class NetworkPort(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )
    label = models.ForeignKey(
        NetworkPortLabel,
        on_delete=models.PROTECT
    )
    mac_address = models.CharField(
        null=True,
        blank=True,
        max_length=17,
        validators=[
            RegexValidator("^([0-9a-fA-F]{2}[:_-]{0,1}){5}[0-9a-fA-F]{2}$",
                           message="Your MAC Address must be in valid hexadecimal format (e.g. 00:1e:c9:ac:78:aa).")
        ]
    )
    connection = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    version = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['asset', 'label', 'version']
        ordering = 'label__order',

    def __str__(self):
        return '{} : {}'.format(self.asset.hostname, self.label.name)

    IDENTITY_FIELDS = ['asset__' + field for field in Asset.IDENTITY_FIELDS] + ['label__name']
