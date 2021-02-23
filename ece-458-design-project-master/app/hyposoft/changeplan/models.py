from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField


class ChangePlan(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=64
    )
    executed = models.BooleanField(
        default=False
    )
    executed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    auto_created = models.BooleanField(
        # This field is used to track changesets that are
        # automatically created when an asset is decommissioned.
        # Used to create a snapshot of a decommissioned asset.
        default=False
    )
    parent = models.ForeignKey(
        # If this change plan is auto_created (i.e. contains a
        # decommissioned asset), this field records the real
        # change plan that it was decommissioned in (or live).
        # This field is null if and only if auto_created is false.
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ['owner', 'name']


class AssetDiff(models.Model):
    changeplan = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )
    live_asset = models.ForeignKey(
        'equipment.Asset',
        related_name='live_asset',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    changed_asset = models.ForeignKey(
        'equipment.Asset',
        related_name='changed_asset',
        on_delete=models.CASCADE
    )
    messages = ArrayField(
        base_field=models.CharField(max_length=512),
        null=True
    )
    conflicts = JSONField(null=True)  # {"field": field, "message": message}[]


class NetworkPortDiff(models.Model):
    changeplan = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )
    live_networkport = models.ForeignKey(
        'network.NetworkPort',
        related_name='live_networkport',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    changed_networkport = models.ForeignKey(
        'network.NetworkPort',
        related_name='changed_networkport',
        null=True,
        on_delete=models.CASCADE
    )
    messages = ArrayField(
        base_field=models.CharField(max_length=512),
        null=True
    )
    conflicts = JSONField(null=True)  # {"field": field, "message": message}[]


class PoweredDiff(models.Model):
    changeplan = models.ForeignKey(
        ChangePlan,
        on_delete=models.CASCADE
    )
    live_powered = models.ForeignKey(
        'power.Powered',
        related_name='live_powered',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    changed_powered = models.ForeignKey(
        'power.Powered',
        related_name='changed_powered',
        on_delete=models.CASCADE,
        null=True
    )
    messages = ArrayField(
        base_field=models.CharField(max_length=512),
        null=True
    )
    conflicts = JSONField(null=True)  # {"field": field, "message": message}[]
