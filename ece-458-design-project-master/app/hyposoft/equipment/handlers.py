from django.db import transaction
from django.db.models import Max
from django.utils.timezone import now
from rest_framework import serializers

from system_log.views import log_decommission
from .models import Asset, Rack
from changeplan.models import ChangePlan
from power.models import Powered, PDU
from network.models import NetworkPortLabel, NetworkPort
from hyposoft.utils import versioned_object, add_asset, add_network_conn, add_rack

"""
Functions to be used by both bulk import and model serializers.
They should be called after validation (signals)

The reason that post-save signals cannot be used is that they
cannot take additional parameters from the serializer as is
required by these functions.
"""


def create_itmodel_extra(itmodel, labels):
    order = 1
    for label in labels:
        if order > itmodel.network_ports:
            break
        NetworkPortLabel.objects.create(
            name=label if len(label) > 0 else str(order),
            itmodel=itmodel,
            order=order
        )
        order += 1


def create_asset_extra(asset, version, power_connections, net_ports):
    # Other objects
    if power_connections:
        order = 1
        for connection in power_connections:
            if order > asset.itmodel.power_ports:
                break
            if isinstance(connection['pdu_id'], int):
                connection['pdu_id'] = PDU.objects.get(id=connection['pdu_id'])
            new_pdu = versioned_object(connection['pdu_id'], version, PDU.IDENTITY_FIELDS)
            if new_pdu is None:
                add_rack(connection['pdu_id'].rack, version)
            Powered.objects.create(
                pdu=versioned_object(connection['pdu_id'], version, PDU.IDENTITY_FIELDS),
                plug_number=connection['plug'],
                version=version,
                asset=asset,
                order=order
            )
            order += 1

    if net_ports:
        i = 1
        for port in net_ports:
            if i > asset.itmodel.network_ports:
                break
            mac = port.get('mac_address')
            if mac and len(mac) == 0:
                mac = None

            if version.id != 0:
                if port['connection'] is not None:
                    versioned_conn = add_network_conn(port['connection'], version)
                    port['connection'] = versioned_conn

            NetworkPort.objects.create(
                asset=asset,
                label=NetworkPortLabel.objects.get(
                    itmodel=asset.itmodel,
                    name=port['label']
                ),
                mac_address=mac,
                connection=add_network_conn(port.get('connection'), version),
                version=version,
            )
            i += 1


def create_rack_extra(rack, version):
    PDU.objects.create(rack=rack, position=PDU.Position.LEFT, version=version)
    PDU.objects.create(rack=rack, position=PDU.Position.RIGHT, version=version)


@transaction.atomic()
def decommission_asset(asset_id, view, user, version):
    try:
        asset = Asset.objects.get(id=asset_id)

        change_plan = ChangePlan.objects.create(
            owner=user,
            name='_DECOMMISSION_' + str(asset.id),
            executed=version.executed,
            executed_at=version.executed_at,
            auto_created=True,
            parent=version
        )

        # Freeze Asset - Copy all data to new change plan
        # Requires resetting of all foreign keys

        old_rack = Rack.objects.get(id=asset.rack.id) if asset.rack else None
        old_asset = Asset.objects.get(id=asset.id)

        asset = add_asset(asset, change_plan)
        rack = asset.rack
        asset.commissioned = None
        asset.decommissioned_by = user
        asset.decommissioned_timestamp = now()
        asset.save()

        if old_rack:
            for a in old_rack.asset_set.exclude(id=old_asset.id):
                add_asset(a, change_plan)

        if rack:
            for pdu in old_rack.pdu_set.filter(version=version):
                new_pdu = rack.pdu_set.get(position=pdu.position)
                for power in pdu.powered_set.filter(asset=old_asset):
                    power.id = None
                    power.pdu = new_pdu
                    power.asset = asset
                    power.version = change_plan
                    power.save()

            def loop_ports(old_asset, recurse):
                for port in old_asset.networkport_set.all():
                    old_port = NetworkPort.objects.get(id=port.id)
                    other = old_port.connection
                    port = add_network_conn(port, change_plan)
                    if other:
                        if recurse:
                            loop_ports(other.asset, False)
                        other = add_network_conn(other, change_plan)
                        other.connection = port
                        port.connection = other
                        other.save()
                        port.save()

            loop_ports(old_asset, True)
        log_decommission(user, old_asset)
        for blade in old_asset.blade_set.all():
            blade.delete()

        if old_asset.version == version:
            old_asset.delete()

        return asset

    except Asset.DoesNotExist:
        raise serializers.ValidationError(
            'Asset does not exist.'
        )
    except ChangePlan.DoesNotExist:
        raise serializers.ValidationError(
            'Change Plan does not exist.'
        )