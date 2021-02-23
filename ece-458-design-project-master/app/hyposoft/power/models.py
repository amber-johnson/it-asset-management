from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from equipment.models import Asset, Rack
from changeplan.models import ChangePlan


class PDU(models.Model):
    assets = models.ManyToManyField(
        "equipment.Asset",
        through='Powered'
    )

    rack = models.ForeignKey(
        Rack,
        on_delete=models.CASCADE
    )

    networked = models.BooleanField()

    class Position(models.TextChoices):
        LEFT = 'L', 'Left'
        RIGHT = 'R', 'Right'

    position = models.CharField(
        choices=Position.choices,
        max_length=16
    )
    version = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['rack', 'position', 'version']

    def __str__(self):
        return "{} PDU on {}".format(
            self.position,
            str(self.rack)
        )

    IDENTITY_FIELDS = ['rack__' + field for field in Rack.IDENTITY_FIELDS] + ['position']


class Powered(models.Model):
    plug_number = models.IntegerField(
        validators=[
            MinValueValidator(1,
                              message="Asset must be plugged into a plug from 1 to 24 on this PDU."),
            MaxValueValidator(24,
                              message="Asset must be plugged into a plug from 1 to 24 on this PDU.")
        ]
    )
    pdu = models.ForeignKey(
        PDU,
        on_delete=models.CASCADE
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )
    on = models.BooleanField(
        default=False
    )
    order = models.IntegerField()

    version = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [['plug_number', 'pdu', 'version'], ['order', 'asset', 'version']]
        ordering = 'asset__asset_number', 'asset_id', 'order'

    IDENTITY_FIELDS = ['pdu__' + field for field in PDU.IDENTITY_FIELDS] + ['plug_number']

    def __str__(self):
        return "Asset {} Power Port {}".format(self.asset, self.order)
