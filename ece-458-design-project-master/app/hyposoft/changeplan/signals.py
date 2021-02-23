from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver

from hyposoft.utils import versioned_equal, versioned_object
from .models import ChangePlan, AssetDiff, NetworkPortDiff, PoweredDiff
from equipment.models import Asset, Rack
from power.models import Powered, PDU
from django.db.models.signals import pre_save


@receiver(user_logged_in)
def create_live(*args, **kwargs):
    if not ChangePlan.objects.filter(id=0).exists():
        ChangePlan.objects.create(id=0, owner=User.objects.filter(username="admin").first(), name="live")


@receiver(pre_save, sender=AssetDiff)
def assetdiff_message(sender, instance, *args, **kwargs):
    messages = []
    conflicts = []
    if instance.live_asset:
        if instance.changed_asset.asset_number != instance.live_asset.asset_number:
            messages.append('OLD ASSET NUMBER: ' + str(instance.live_asset.asset_number) + ' | ' +
                            'NEW ASSET NUMBER: ' + str(instance.changed_asset.asset_number))
        if instance.changed_asset.hostname != instance.live_asset.hostname:
            messages.append('OLD HOSTNAME: ' + str(instance.live_asset.hostname) + ' | ' +
                            'NEW HOSTNAME: ' + str(instance.changed_asset.hostname))

        if instance.changed_asset.site != instance.live_asset.site:
            messages.append('OLD SITE: ' + instance.live_asset.site.name + ' | ' +
                            'NEW SITE: ' + instance.changed_asset.site.name)

        if instance.live_asset.commissioned == Asset.Decommissioned.COMMISSIONED \
                and instance.changed_asset.commissioned is None:
            messages.append('DECOMMISSION ASSET' +
                            (': ' + instance.live_asset.hostname) if instance.live_asset.hostname else '')

        if not instance.changed_asset.site.offline:
            if not instance.live_asset.site.offline:
                if not versioned_equal(instance.changed_asset.rack, instance.live_asset.rack, Rack.IDENTITY_FIELDS):
                    messages.append('OLD RACK: ' + str(
                        instance.live_asset.rack.rack) + ' | ' +  # todo test if new rack create in change plan breaks this
                                    'NEW RACK: ' + str(instance.changed_asset.rack.rack))
            else:
                messages.append('NEW RACK: ' + str(instance.changed_asset.rack.rack))

        if not instance.changed_asset.site.offline and instance.changed_asset.itmodel.type != 'blade':
            if not instance.live_asset.site.offline and instance.live_asset.itmodel.type != 'blade':
                if instance.changed_asset.rack_position != instance.live_asset.rack_position:
                    messages.append('OLD RACK POSITION: ' + str(instance.live_asset.rack_position) + ' | ' +
                                    'NEW RACK POSITION: ' + str(instance.changed_asset.rack_position))
            else:
                messages.append('NEW RACK POSITION: ' + str(instance.changed_asset.rack_position))

        if instance.changed_asset.itmodel != instance.live_asset.itmodel:
            messages.append('OLD ITMODEL: ' + str(instance.live_asset.itmodel) + ' | ' +
                            'NEW ITMODEL: ' + str(instance.changed_asset.itmodel))
        if instance.changed_asset.owner != instance.live_asset.owner:
            messages.append(('OLD OWNER: ' + ((str(instance.live_asset.owner.username))
                                              if instance.live_asset.owner else 'None')) + ' | ' +
                            ('NEW OWNER: ' + (str(instance.changed_asset.owner.username)
                                              if instance.changed_asset.owner else 'None')))

        # display_color, cpu, memory, storage
        def get_upgrades(attr):
            if getattr(instance.live_asset, attr) is not None:
                old_val = getattr(instance.live_asset, attr)
            else:
                old_val = getattr(instance.live_asset.itmodel, attr)
            if getattr(instance.changed_asset, attr) is not None:
                new_val = getattr(instance.changed_asset, attr)
            else:
                new_val = getattr(instance.changed_asset.itmodel, attr)

            return old_val, new_val

        old_display_color, new_display_color = get_upgrades('display_color')
        if old_display_color != new_display_color:
            messages.append('OLD DISPLAY COLOR: ' + str(old_display_color) + ' | ' +
                            'NEW DISPLAY COLOR: ' + str(new_display_color))
        old_cpu, new_cpu = get_upgrades('cpu')
        if old_cpu != new_cpu:
            messages.append('OLD CPU: ' + (str(old_cpu) or 'None') + ' | ' +
                            'NEW CPU: ' + (str(new_cpu) or 'None'))
        old_storage, new_storage = get_upgrades('storage')
        if old_storage != new_storage:
            messages.append('OLD STORAGE: ' + (str(old_storage) or 'None') + ' | ' +
                            'NEW STORAGE: ' + (str(new_storage) or 'None'))
        old_memory, new_memory = get_upgrades('memory')
        if old_memory != new_memory:
            messages.append('OLD MEMORY: ' + str(old_memory) + ' | ' +
                            'NEW MEMORY: ' + str(new_memory))

        if instance.live_asset.commissioned is None and instance.changed_asset.commissioned is not None:
            conflicts.append({"field": "decommissioned",
                              "message": 'Live asset is decommissioned.'})

        # blade_chassis
        if instance.changed_asset.itmodel.type == 'blade':
            if not versioned_equal(
                    instance.changed_asset.blade_chassis, instance.live_asset.blade_chassis, Asset.IDENTITY_FIELDS):
                messages.append('OLD BLADE CHASSIS: ' + str(instance.live_asset.blade_chassis) + ' | ' +
                                'NEW BLADE CHASSIS: ' + str(instance.changed_asset.blade_chassis))
            # slot
            if instance.changed_asset.slot != instance.live_asset.slot:
                messages.append('OLD SLOT: ' + str(instance.live_asset.slot) + ' | ' +
                                'NEW SLOT: ' + str(instance.changed_asset.slot))

    else:
        changed = instance.changed_asset
        messages.append('CREATE ASSET: {} in {}{}'.format(
            str(changed) if str(changed) != '' and str(changed) != 'None' else str(changed.itmodel),
            changed.site.name + ' ' + changed.rack.rack if changed.rack is not None else changed.site.name,
            'U' + str(changed.rack_position) if changed.rack_position is not None else ''
        ))

    asset = instance.changed_asset
    if asset.rack_position is not None and asset.commissioned == Asset.Decommissioned.COMMISSIONED:
        blocked = Asset.objects.filter(
            rack=asset.rack,
            rack_position__range=(asset.rack_position,
                                  asset.rack_position + asset.itmodel.height - 1),
            site=asset.site,
            version_id=0
        )
        if len(blocked) > 0:
            conflicts.append({"field": "rack_position",
                              "message": 'There is already an asset in this area of the specified rack.'})
        i = asset.rack_position - 1
        while i > 0:
            live_rack = versioned_object(asset.rack, ChangePlan.objects.get(id=0),
                                         Rack.IDENTITY_FIELDS)
            under = Asset.objects.filter(
                rack=live_rack,
                rack_position=i,
                site=asset.site,
                version_id=0
            )
            if asset.asset_number is not None:
                under = under.exclude(asset_number=asset.asset_number)
            if len(under) > 0:
                other = under.values_list(
                    'rack_position', 'itmodel__height')[0]
                if other[0] + other[1] > asset.rack_position:
                    conflicts.append({"field": "rack_position",
                                      "message": 'There is already an asset in this area of the specified rack.'})
            i -= 1
    instance.messages = messages
    instance.conflicts = conflicts


@receiver(pre_save, sender=NetworkPortDiff)
def networkportdiff_message(sender, instance, *args, **kwargs):
    messages = []
    conflicts = []
    if instance.live_networkport:
        if not instance.changed_networkport:
            messages.append('UNPLUG PORT: ' + str(instance.live_networkport.label.name))
        else:
            if instance.changed_networkport.label != instance.live_networkport.label:
                messages.append('OLD LABEL: ' + str(instance.live_networkport.label.name) + ' | ' +
                                'NEW LABEL: ' + str(instance.changed_networkport.label.name))
            if instance.changed_networkport.mac_address != instance.live_networkport.mac_address:
                messages.append('OLD MAC ADDRESS: ' + str(instance.live_networkport.mac_address) + ' | ' +
                                'NEW MAC ADDRESS: ' + str(instance.changed_networkport.mac_address))
            if not versioned_equal(instance.live_networkport, instance.changed_networkport, ['asset__hostname', 'label__name']):
                messages.append('OLD CONNECTION: ' + (str(instance.live_networkport.connection.asset) + ' ' +
                                                      str(instance.live_networkport.connection.label.name)
                                                      if instance.live_networkport.connection else 'None') + ' | ' +
                                ('NEW CONNECTION: ' + str(instance.changed_networkport.connection.asset) + ' ' +
                                 str(instance.changed_networkport.connection.label.name)
                                 if instance.changed_networkport.connection else 'None'))

    else:
        messages.append('CREATE NETWORKPORT CONNECTION: {} – {} {}'.format(
            instance.changed_networkport.asset,
            instance.changed_networkport.label.name,
            instance.changed_networkport.mac_address or ""
        ) + (" TO {} – {}".format(
            instance.changed_networkport.connection.asset,
            instance.changed_networkport.connection.label.name) if instance.changed_networkport.connection else ''
             ))

    if instance.changed_networkport and instance.changed_networkport.connection:
        if instance.changed_networkport.connection and \
                instance.changed_networkport.asset == instance.changed_networkport.connection.asset:
            conflicts.append({"field": "network_port",
                              "message": 'Connections must be between different assets.'})
        if instance.changed_networkport.connection and \
                instance.changed_networkport.connection.asset.site != instance.changed_networkport.asset.site:
            conflicts.append({"field": "network_port",
                              "message": 'Connections must in the same datacenter.'})
        if instance.changed_networkport.connection and \
                instance.changed_networkport.connection.connection is not None and \
                instance.changed_networkport.connection.connection.id != instance.changed_networkport.id:
            conflicts.append({"field": "network_port",
                              "message": '{} is already connected to {} on {}'.format(
                                  instance.changed_networkport.connection.asset,
                                  instance.changed_networkport.connection.connection.asset,
                                  instance.changed_networkport.connection.label.name
                              )})

    instance.messages = messages
    instance.conflicts = conflicts


@receiver(pre_save, sender=PoweredDiff)
def powereddiff_message(sender, instance, *args, **kwargs):
    messages = []
    conflicts = []
    if instance.live_powered:
        if not instance.changed_powered:
            messages.append('UNPLUG POWER: ASSET {} FROM PORT {}{}'.format(
                instance.live_powered.asset.asset_number or instance.changed_powered.asset,
                instance.live_powered.pdu.position,
                instance.live_powered.plug_number
            ))
            instance.messages = messages
            instance.conflicts = conflicts
            return
        if instance.changed_powered.plug_number != instance.live_powered.plug_number:
            messages.append('OLD PLUG NUMBER: ' + str(instance.live_powered.plug_number) + ' | ' +
                            'NEW PLUG NUMBER: ' + str(instance.changed_powered.plug_number))
        if not versioned_equal(instance.changed_powered.pdu, instance.live_powered.pdu, PDU.IDENTITY_FIELDS):
            messages.append('OLD PDU: ' + str(instance.live_powered.pdu.rack.rack) + ' ' +
                            str(instance.live_powered.pdu.position) + ' | ' +
                            'NEW PDU: ' + str(instance.changed_powered.pdu.rack.rack) + ' ' +
                            str(instance.changed_powered.pdu.position))
    else:
        messages.append('SET POWER PLUG: ASSET {} TO PORT {}{}'.format(
            instance.changed_powered.asset.asset_number or instance.changed_powered.asset,
            instance.changed_powered.pdu.position,
            instance.changed_powered.plug_number
        ))

    num_powered = len(Powered.objects.filter(asset=instance.changed_powered.asset))
    if instance.changed_powered not in Powered.objects.all() and num_powered == instance.changed_powered.asset.itmodel.power_ports:
        conflicts.append({"field": "power_port",
                          "message": 'All the power port connections have already been used.'})
    if instance.changed_powered.pdu.assets.count() > 24:
        conflicts.append({"field": "power_port",
                          "message": 'This PDU is already full.'})
    if instance.changed_powered.pdu.rack != instance.changed_powered.asset.rack:
        conflicts.append({"field": "power_port",
                          "message": 'PDU must be on the same rack as the asset.'})
    instance.messages = messages
    instance.conflicts = conflicts
