from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import PDU, Powered
from .views import get_pdu

from rest_framework import serializers


@receiver(pre_save, sender=Powered)
def check_pdu(sender, instance, *args, **kwargs):
    num_powered = len(Powered.objects.filter(asset=instance.asset))
    if instance not in Powered.objects.all() and num_powered == instance.asset.itmodel.power_ports:
        raise serializers.ValidationError("All the power port connections have already been used.")
    if instance.pdu.assets.count() > 24:
        raise serializers.ValidationError("This PDU is already full.")
    if instance.pdu.rack != instance.asset.rack:
        raise serializers.ValidationError(
            "PDU must be on the same rack as the asset.")


@receiver(pre_save, sender=PDU)
def set_connected(sender, instance, *args, **kwargs):
    if instance.rack.site.abbr.lower() == 'rtp1':
        response = get_pdu(instance.rack.rack, instance.position)
        instance.networked = response[1] < 400
    else:
        instance.networked = False
