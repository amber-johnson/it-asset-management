import threading
import time

from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from system_log.models import ActionLog, display_name, username
from .models import *
from .handlers import get_pdu, post_pdu, is_blade_power_on, set_blade_power

@api_view()
def get_asset(request, asset_id):
    networked = False
    powered = False

    asset = Asset.objects.get(id=asset_id)

    if not request.user.is_superuser:
        if not (request.user.permission.power_perm or request.user == asset.owner):
            raise serializers.ValidationError("You don't have permission.")

    if not asset.site.offline:
        if asset.itmodel.type == "blade":
            networked = True
            powered = is_blade_power_on(asset.blade_chassis.hostname, asset.slot)
        else:
            rack = asset.rack.rack
            ports = Powered.objects.filter(asset=asset)
            for port in ports: 
                res = get_pdu(rack, port.pdu.position)
                if res[1] < 400:
                    networked = True
                    state = dict(res[0])
                    if state.get(str(port.plug_number)) == "ON":
                        powered = True

    if networked:
        return Response("On" if powered else "Off", HTTP_200_OK)
    else:
        return Response("Unavailable", HTTP_200_OK)


def log(user, instance, old, new):
    if old == new: return

    ActionLog.objects.create(
        action=ActionLog.Action.UPDATE,
        username=username(user),
        display_name=display_name(user),
        model=instance.__class__.__name__,
        instance_id=instance.id,
        field_changed="state",
        old_value=old,
        new_value=new
    )


@api_view(['POST'])
def post_asset(request):
    asset = Asset.objects.get(id=request.data['asset_id'])
    if not request.user.is_superuser:
        if not (request.user.permission.power_perm or request.user == asset.owner):
            raise serializers.ValidationError("You don't have permission.")
    if request.data['state'].lower() not in ("on", "off"):
        raise serializers.ValidationError(
            "Powered state must be either 'on' or 'off'"
        )
    state = request.data['state'].lower()

    if not asset.site.offline:
        if asset.itmodel.type == "blade":
                old = "ON" if is_blade_power_on(asset.blade_chassis.hostname, asset.slot) else "OFF"
                set_blade_power(asset.blade_chassis.hostname, asset.slot, state)
                log(request.user, asset, old, state.upper())
        else:
            rack = asset.rack.rack
            ports = Powered.objects.filter(asset=asset)

            for port in ports: 
                res = post_pdu(rack, port.pdu.position, port.plug_number, state)
                if res[1] < 400:
                    old = "ON" if port.on else "OFF"
                    port.on = state.upper() == 'ON'
                    port.save()
                    log(request.user, port, old, state.upper())


    return Response(HTTP_204_NO_CONTENT)


@api_view(['POST'])
def cycle_asset(request):
    threads = []

    asset = Asset.objects.get(id=request.data['asset_id'])

    if not request.user.is_superuser:
        if not (request.user.permission.power_perm or request.user == asset.owner):
            raise serializers.ValidationError("You don't have permission.")

    if not asset.site.offline:
        if asset.itmodel.type == "blade":
            networked = True
            old = "ON" if is_blade_power_on(asset.blade_chassis.hostname, asset.slot) else "OFF"
            set_blade_power(asset.blade_chassis.hostname, asset.slot, "off")
            time.sleep(2)
            set_blade_power(asset.blade_chassis.hostname, asset.slot, "on")
            log(request.user, asset, old, "CYCLED")
        else:
            rack = asset.rack.rack
            ports = Powered.objects.filter(asset=asset)
            for port in ports: 
                res = post_pdu(rack, port.pdu.position, port.plug_number, 'off')

                if res[1] < 400:
                    old = "ON" if port.on else "OFF"
                    port.on = False
                    port.save()
                    log(request.user, port, old, "CYCLED")

                def delay_start(rack, position, port):
                    time.sleep(2)
                    res = post_pdu(rack, position, port.plug_number, 'on')
                    if res[1] < 400:
                        port.on = True
                        port.save()

                t = threading.Thread(target=delay_start, args=(rack, port.pdu.position, port))
                threads.append(t)
                t.start()


    for thread in threads:
        thread.join()
    return Response(HTTP_204_NO_CONTENT)
