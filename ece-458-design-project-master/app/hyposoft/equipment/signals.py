from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import ITModel, Asset, Site

from rest_framework import serializers

"""
Signals used for additional validation.

All business logic previously in a signal has been
moved to handlers.py.
"""


@receiver(pre_save, sender=Site)
def check_global(instance, *args, **kwargs):
    if instance.name == 'Global' or instance.abbr == 'Global':
        raise serializers.ValidationError(
            "Global is a reserved name. You cannot create a site called Global."
        )


@receiver(pre_save, sender=ITModel)
def check_deployed_assets(sender, instance, *args, **kwargs):
    if instance.asset_set.count() == 0:
        return

    def throw():
        raise serializers.ValidationError(
            "Cannot modify interconnected ITModel attributes while assets are deployed."
        )

    try:
        old = ITModel.objects.get(id=instance.id)
        if old.power_ports != instance.power_ports:
            throw()
        if old.network_ports != instance.network_ports:
            throw()
        if old.height != instance.height:
            throw()

    except ITModel.DoesNotExist:
        pass


@receiver(pre_save, sender=Asset)
def validate_asset(sender, instance, *args, **kwargs):
    # Fields
    if instance.site is not None and instance.rack is not None and instance.site != instance.rack.site:
        raise serializers.ValidationError(
            "Asset datacenter cannot be different from rack datacenter.")

    if instance.itmodel.type == ITModel.Type.BLADE and instance.blade_chassis is not None\
            and instance.blade_chassis.itmodel.type != ITModel.Type.CHASSIS:
        raise serializers.ValidationError(
            "Blade must reference Blade Chassis asset."
        )

    if instance.asset_number is not None:
        if instance.asset_number > 999999:
            raise serializers.ValidationError(
                "The asset number is too large. Please try manually setting it to be 6 digits.")

        if instance.asset_number < 100000:
            raise serializers.ValidationError(
                "The asset number is too small. Please try manually setting it to be 6 digits.")

    if instance.rack is None or instance.rack_position is None:
        if not (instance.site.offline or instance.itmodel.type == ITModel.Type.BLADE):
            raise serializers.ValidationError(
                "If asset is being placed in a datacenter, rack and rack position must be specified."
            )
    else:
        if 42 < instance.rack_position + instance.itmodel.height - 1:
            raise serializers.ValidationError(
                "The asset does not fit on the specified rack from the given position.")

        if instance.rack.decommissioned:
            raise serializers.ValidationError(
                "The rack does not exist, please create it first.")

        blocked = Asset.objects.filter(
            rack=instance.rack,
            rack_position__range=(instance.rack_position,
                                  instance.rack_position + instance.itmodel.height - 1),
            site=instance.site,
            version=instance.version
        ).exclude(id=instance.id)

        if len(blocked) > 0:
            raise serializers.ValidationError(
                "There is already an asset in this area of the specified rack.")

        i = instance.rack_position - 1
        while i > 0:
            under = Asset.objects.filter(
                rack=instance.rack,
                rack_position=i,
                site=instance.site,
                version=instance.version
            ).exclude(id=instance.id)
            if len(under) > 0:
                asset = under.values_list(
                    'rack_position', 'itmodel__height')[0]
                if asset[0] + asset[1] > instance.rack_position:
                    raise serializers.ValidationError(
                        "There is already an asset in this area of the specified rack.")
                else:
                    break
            i -= 1

        if instance.hostname is not None and len(instance.hostname) == 0:
            instance.hostname = None

        if instance.hostname is None and instance.networkport_set.exclude(connection__isnull=True).exists():
            raise serializers.ValidationError(
                "If network port connections are set, hostname must be set."
            )


# Added this in to_internal since I actually send .rack even for blades 
# Also this prevents me from adding offline assets, since it wouldn't have any racks

# @receiver(post_save, sender=Asset)
# def set_asset_defaults(instance, created, *args, **kwargs):
#     if instance.itmodel.type == ITModel.Type.BLADE and instance.rack is None:
#         instance.rack = instance.blade_chassis.rack
#         instance.save()


