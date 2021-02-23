from django.db import transaction

from equipment.models import Asset, Rack, ITModel
from equipment.handlers import decommission_asset
from network.models import NetworkPort
from power.models import Powered, PDU
from hyposoft.utils import versioned_object, add_network_conn, add_rack, add_asset, newest_object
from .models import AssetDiff, NetworkPortDiff, PoweredDiff, ChangePlan


def create_asset_diffs(changeplan, target):
    changed_assets = Asset.objects.filter(version=changeplan).order_by('id')
    for changed_asset in changed_assets:
        try:
            live_asset = versioned_object(changed_asset, target, Asset.IDENTITY_FIELDS)
            if live_asset is None:
                live_asset = versioned_object(changed_asset, target, ['hostname'])
            AssetDiff.objects.create(
                changeplan=changeplan,
                live_asset=live_asset,
                changed_asset=changed_asset,
            )
        except Asset.DoesNotExist:
            AssetDiff.objects.create(
                changeplan=changeplan,
                changed_asset=changed_asset,
            )
    for child in changeplan.changeplan_set.all():
        asset = Asset.objects.filter(commissioned=None, version=child).first()
        if asset:
            old = newest_object(Asset, changeplan, asset_number=asset.asset_number, hostname=asset.hostname)
            AssetDiff.objects.create(
                changeplan=changeplan,
                live_asset=old,
                changed_asset=asset
            )


def create_networkport_diffs(changeplan, target):
    for asset in Asset.objects.filter(version=changeplan).order_by('id'):
        live_asset = versioned_object(asset, target, ['hostname'])
        new_ports = asset.networkport_set.all()
        id_fields = ['asset__hostname', 'label__name']
        if live_asset:
            live_ports = live_asset.networkport_set.all()
            for port in live_ports:
                if versioned_object(port, changeplan, id_fields) not in new_ports:
                    NetworkPortDiff.objects.create(
                        changeplan=changeplan,
                        live_networkport=port,
                        changed_networkport=None
                    )
        for port in new_ports:
            live_port = versioned_object(port, target, id_fields)
            NetworkPortDiff.objects.create(
                changeplan=changeplan,
                changed_networkport=port,
                live_networkport=live_port
            )

def create_powered_diffs(changeplan, target):
    for asset in Asset.objects.filter(version=changeplan).order_by('id'):
        live_asset = versioned_object(asset, target, Asset.IDENTITY_FIELDS)
        new_plugs = asset.powered_set.all()
        if live_asset:
            live_plugs = live_asset.powered_set.all()
            for plug in live_plugs:
                if versioned_object(plug, changeplan, Powered.IDENTITY_FIELDS) not in new_plugs:
                    PoweredDiff.objects.create(
                        changeplan=changeplan,
                        live_powered=plug,
                        changed_powered=None
                    )
        for plug in new_plugs:
            live_plug = versioned_object(plug, target, Powered.IDENTITY_FIELDS)
            PoweredDiff.objects.create(
                changeplan=changeplan,
                changed_powered=plug,
                live_powered=live_plug
            )


def execute_assets(changeplan):
    changed_assets = Asset.objects.filter(version=changeplan).order_by('itmodel__type')
    for changed_asset in changed_assets:
        try:
            live = ChangePlan.objects.get(id=0)
            live_asset = versioned_object(changed_asset, live, Asset.IDENTITY_FIELDS)
            if live_asset is None:
                live_asset = versioned_object(changed_asset, live, ['hostname'])

            if live_asset is None:
                Asset.objects.create(
                    version=live,
                    hostname=changed_asset.hostname,
                    site=changed_asset.site,
                    rack=add_rack(changed_asset.rack, live) if not changed_asset.site.offline else None,
                    rack_position=changed_asset.rack_position if not changed_asset.site.offline and changed_asset.itmodel.type != ITModel.Type.BLADE else None,
                    itmodel=changed_asset.itmodel,
                    owner=changed_asset.owner,
                    comment=changed_asset.comment,
                    display_color=changed_asset.display_color if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None,
                    cpu=changed_asset.cpu if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None,
                    memory=changed_asset.memory if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None,
                    storage=changed_asset.storage if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None,
                    blade_chassis=add_asset(changed_asset.blade_chassis, live, Asset.IDENTITY_FIELDS)\
                    if changed_asset.itmodel.type == ITModel.Type.BLADE or changed_asset.itmodel.type == ITModel.Type.CHASSIS else None,
                    slot=changed_asset.slot if changed_asset.itmodel.type == ITModel.Type.CHASSIS else None
                )

            else:
                live_asset.asset_number = changed_asset.asset_number
                live_asset.hostname = changed_asset.hostname
                live_asset.site = changed_asset.site
                live_asset.rack = add_rack(changed_asset.rack, live) if not changed_asset.site.offline else None
                live_asset.rack_position = changed_asset.rack_position if not changed_asset.site.offline and changed_asset.itmodel.type != ITModel.Type.BLADE else None
                live_asset.itmodel = changed_asset.itmodel
                live_asset.owner = changed_asset.owner
                live_asset.comment = changed_asset.comment
                live_asset.display_color = changed_asset.display_color if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None
                live_asset.cpu = changed_asset.cpu if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None
                live_asset.memory = changed_asset.memory if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None
                live_asset.storage = changed_asset.storage if changed_asset.itmodel.type != ITModel.Type.CHASSIS else None
                live_asset.blade_chassis = add_asset(changed_asset.blade_chassis, live, Asset.IDENTITY_FIELDS)\
                    if changed_asset.itmodel.type == ITModel.Type.BLADE else None
                live_asset.slot = changed_asset.slot if changed_asset.itmodel.type == ITModel.Type.BLADE else None
                live_asset.save()
        except Exception as e:
            pass


def execute_networkports(changeplan):
    changed_networkports = NetworkPort.objects.filter(version=changeplan)
    for changed_networkport in changed_networkports:
        try:
            live = ChangePlan.objects.get(id=0)
            live_networkport = versioned_object(changed_networkport, live, NetworkPort.IDENTITY_FIELDS)

            if live_networkport is None:
                live_asset = add_asset(changed_networkport.asset, live)
                NetworkPort.objects.create(
                    asset=live_asset,
                    label=changed_networkport.label,
                    mac_address=changed_networkport.mac_address,
                    connection=add_network_conn(changed_networkport.connection, live),
                    version=live
                )
            else:
                live_networkport.label = changed_networkport.label
                live_networkport.mac_address = changed_networkport.mac_address
                if changed_networkport.connection:
                    live_networkport.connection = add_network_conn(changed_networkport.connection, live)
                else:
                    live_networkport.connection = None
                live_networkport.save()

        except Exception as e:
            pass


def execute_powereds(changeplan):
    changed_powereds = Powered.objects.filter(version=changeplan)
    for changed_powered in changed_powereds:
        try:
            live = ChangePlan.objects.get(id=0)
            live_powered = versioned_object(changed_powered, live, Powered.IDENTITY_FIELDS)

            live_powered.plug_number = changed_powered.plug_number
            live_powered.pdu = versioned_object(changed_powered.pdu, live, PDU.IDENTITY_FIELDS)
            new_asset = versioned_object(changed_powered.asset, live, Asset.IDENTITY_FIELDS)
            if new_asset is None:
                new_asset = versioned_object(changed_powered.asset, live, ['hostname'])
            live_powered.asset = new_asset
            live_powered.on = changed_powered.on
            live_powered.order = changed_powered.order
            live_powered.save()

        except:
            pass


def get_asset(changeplan, target):
    if changeplan:
        if not changeplan.executed:
            create_asset_diffs(changeplan, target)

        asset_diffs = AssetDiff.objects.filter(changeplan=changeplan).order_by('id')
        diffs = [
            {
                "changeplan": asset_diff.changeplan.name,
                "messages": asset_diff.messages,
                "conflicts": asset_diff.conflicts,
                "live": asset_diff.live_asset,
                "new": asset_diff.changed_asset
            }
            for asset_diff in asset_diffs
        ]

        if not changeplan.executed:
            AssetDiff.objects.filter(changeplan=changeplan).delete()  # Make sure we recalculate diff every request
        return diffs
    else:
        return []


def get_network(changeplan, target):
    if changeplan:
        if not changeplan.executed:
            create_networkport_diffs(changeplan, target)
        networkport_diffs = NetworkPortDiff.objects.filter(changeplan=changeplan)
        diffs = [
            {
                "changeplan": networkport_diff.changeplan.name,
                "messages": networkport_diff.messages,
                "conflicts": networkport_diff.conflicts,
                "live": networkport_diff.live_networkport,
                "new": networkport_diff.changed_networkport
            }
            for networkport_diff
            in networkport_diffs
        ]
        if not changeplan.executed:
            NetworkPortDiff.objects.filter(changeplan=changeplan).delete()
        return diffs
    else:
        return []


def get_power(changeplan, target):
    if changeplan:
        if not changeplan.executed:
            create_powered_diffs(changeplan, target)
        powered_diffs = PoweredDiff.objects.filter(changeplan=changeplan).order_by('id')
        diffs = [
            {
                "changeplan": powered_diff.changeplan.name,
                "messages": powered_diff.messages,
                "conflicts": powered_diff.conflicts,
                "live": powered_diff.live_powered,
                "new": powered_diff.changed_powered
            }
            for powered_diff
            in powered_diffs
        ]
        if not changeplan.executed:
            PoweredDiff.objects.filter(changeplan=changeplan).delete()
        return diffs
    else:
        return []
