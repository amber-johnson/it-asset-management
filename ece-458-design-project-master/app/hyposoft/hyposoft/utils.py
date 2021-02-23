from copy import deepcopy

from django.db.models import Q
from rest_framework import serializers

from equipment.models import Rack, Asset
from changeplan.models import ChangePlan
from power.models import PDU


# Given a rack row letter, provides the next row letter
# Essentially, after Z is AA and after AA is AB etc.
def next_char(char):
    if len(char) == 1:
        if char < "Z":
            return chr(ord(char) + 1)
        else:
            return "AA"
    else:
        if char[-1] < "Z":
            return char[:-1] + next_char(char[-1])
        else:
            return next_char(char[:-1]) + "A"


# Returns whether rack row1 is greater than rack row2.
# AA is greater than Z, etc. Otherwise, use lexographic comparison.
def greater_than(row1, row2):
    if len(row2) > len(row1):
        return False
    return row1 > row2


def generate_racks(r1, r2, c1, c2):
    r1 = r1.upper()
    r2 = r2.upper()
    if greater_than(r1, r2):
        temp = r1
        r1 = r2
        r2 = temp

    c1 = int(c1)
    c2 = int(c2)

    racks = []

    for c in range(min(c1, c2), max(c1, c2) + 1):
        r = r1
        while True:
            racks.append(r + str(c))
            r = next_char(r)
            if greater_than(r, r2):
                break

    return racks


def get_version(request):
    val = request.META.get('HTTP_X_CHANGE_PLAN', 0)
    try:
        return int(val)
    except:
        return 0


def get_site(request):
    val = request.META.get('HTTP_X_SITE', None)
    try:
        return int(val)
    except:
        return None


def newest_object(model, version, **filters):
    try:
        return model.objects.get(version=version, **filters)
    except:
        if version.parent is not None:
            try:
                return model.objects.get(version=version.parent, **filters)
            except:
                pass
        try:
            return model.objects.get(version=ChangePlan.objects.get(id=0), **filters)
        except:
            return None


def versioned_object(obj, version, identity_fields):
    if obj.version == version:
        return obj
    obj_list = obj.__class__.objects.filter(id=obj.id).values(*identity_fields)[0]
    if any([v is None for v in obj_list.values()]):
        return None
    result = obj.__class__.objects.filter(version=version, **obj_list).first()
    if result is None:
        for child in version.changeplan_set.all():
            decom = obj.__class__.objects.filter(version=child, **obj_list).first()
            if decom is not None:
                result = decom
                break
    return result


def versioned_queryset(queryset, version, identity_fields):
    if version.id == 0:
        return queryset.filter(version=version)
    try:
        versioned = queryset.filter(version=version)
        values = versioned.values_list(*identity_fields)
        q = Q()
        for item in values:
            d = {}
            for i in range(len(identity_fields)):
                d[identity_fields[i]] = item[i]
            q = q | Q(**d)

        # Return all objects in live, except for objects that exist separately in the change plan
        return queryset.filter(version_id=0).exclude(q).union(versioned)

    except:
        return queryset


def versioned_equal(obj1, obj2, identity_fields):
    for field in identity_fields:
        attrs = field.split("__")
        obj1v = obj1
        obj2v = obj2
        for attr in attrs:
            obj1v = getattr(obj1v, attr)
            obj2v = getattr(obj2v, attr)
        if obj1v != obj2v:
            return False
    return True


# For adding various objects from live to a change plan
def add_rack(rack, change_plan):
    if rack.version == change_plan:
        return rack
    newer_rack = versioned_object(rack, change_plan, Rack.IDENTITY_FIELDS)
    if newer_rack:
        return newer_rack
    rack = deepcopy(rack)
    rack.id = None
    rack.version = change_plan
    rack.save()
    PDU.objects.create(rack=rack, position=PDU.Position.LEFT, version=change_plan)
    PDU.objects.create(rack=rack, position=PDU.Position.RIGHT, version=change_plan)
    return rack


def add_asset(asset, change_plan, identity_fields=Asset.IDENTITY_FIELDS):
    if asset.rack and asset.rack.version != asset.version:
        asset.rack = add_rack(asset.rack, asset.version)
    if asset.version == change_plan:
        return asset
    newer_asset = versioned_object(asset, change_plan, identity_fields)
    if newer_asset:
        return newer_asset
    rack = None
    if asset.rack:
        rack = versioned_object(asset.rack, change_plan, Rack.IDENTITY_FIELDS)
        if rack is None:
            rack = add_rack(asset.rack, change_plan)

    old_asset = Asset.objects.get(id=asset.id)
    asset.id = None
    asset.version = change_plan
    asset.rack = rack
    asset.save()

    if asset.blade_chassis is not None:
        asset.blade_chassis = add_asset(asset.blade_chassis, change_plan, identity_fields)

    for blade in old_asset.blade_set.all():
        add_asset(blade, change_plan, identity_fields)

    return asset


def add_network_conn(connection, version):
    if connection is None:
        return None
    versioned_conn = versioned_object(connection, version, ['asset__hostname', 'label'])
    if versioned_conn is None:
        # Add connected asset to change plan
        conn_asset = connection.asset
        if conn_asset.hostname is None:
            raise serializers.ValidationError(
                "Hostname of an asset with network connections must be set"
            )
        new_asset = add_asset(conn_asset, version, identity_fields=['hostname'])
        connection.id = None
        connection.asset = new_asset
        connection.connection = None
        connection.version = version
        connection.save()
        return connection
    return versioned_conn
