from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Max
from import_export import resources, fields
from import_export.resources import ModelResource
from rest_framework import serializers

from equipment.handlers import create_itmodel_extra, create_asset_extra
from changeplan.models import ChangePlan
from hypo_auth.handlers import check_asset_perm
from hyposoft.utils import versioned_object, add_asset, add_rack, newest_object
from .models import ITModel, Asset, Rack, Site
from network.models import NetworkPortLabel
from power.models import Powered, PDU
from import_export.widgets import ForeignKeyWidget, Widget, NumberWidget, IntegerWidget

import re


class VersionedResource(resources.ModelResource):
    def __init__(self, version, owner, force=False):
        super(VersionedResource, self).__init__()
        self.version = ChangePlan.objects.get(id=version)
        self.owner = owner
        self.force = force
        if not force:
            self.version = self.get_new_version()

    def get_new_version(self):
        if self.force:
            new_version = ChangePlan.objects.get(id=self.version.id)
        else:
            parent = ChangePlan.objects.get(id=self.version.id)
            try:
                new_version = ChangePlan.objects.get(
                    owner=self.owner,
                    name="_BULK_IMPORT_" + str(id(self))
                )
            except ChangePlan.DoesNotExist:
                new_version = ChangePlan.objects.create(
                    owner=self.owner,
                    name="_BULK_IMPORT_" + str(id(self)),
                    executed=False,
                    auto_created=True,
                    parent=parent
                )
        return new_version


class ITModelResource(ModelResource):
    mount_type = fields.Field(
        attribute='type'
    )
    network_port_name_1 = fields.Field(attribute='network_port_name_1')
    network_port_name_2 = fields.Field(attribute='network_port_name_2')
    network_port_name_3 = fields.Field(attribute='network_port_name_3')
    network_port_name_4 = fields.Field(attribute='network_port_name_4')

    def skip_row(self, instance, original):
        port1 = getattr(instance, "network_port_name_1")
        port2 = getattr(instance, "network_port_name_2")
        port3 = getattr(instance, "network_port_name_3")
        port4 = getattr(instance, "network_port_name_4")
        new = [port for port in (port1, port2, port3, port4) if len(port) > 0]
        curr = original.networkportlabel_set.values_list("name", flat=True)

        if sorted(new) != sorted(curr):
            return False

        delattr(instance, "network_port_name_1")
        delattr(instance, "network_port_name_2")
        delattr(instance, "network_port_name_3")
        delattr(instance, "network_port_name_4")
        return super(ITModelResource, self).skip_row(instance, original)

    def dehydrate_network_port_name_1(self, itmodel):
        try:
            if itmodel.network_ports >= 1:
                my_network_port_label = NetworkPortLabel.objects.get(itmodel=itmodel, order=1)
                return my_network_port_label.name
            else:
                return ''
        except:
            return ''

    def dehydrate_network_port_name_2(self, itmodel):
        try:
            if itmodel.network_ports >= 2:
                my_network_port_label = NetworkPortLabel.objects.get(itmodel=itmodel, order=2)
                return my_network_port_label.name
            else:
                return ''
        except:
            return ''

    def dehydrate_network_port_name_3(self, itmodel):
        try:
            if itmodel.network_ports >= 3:
                my_network_port_label = NetworkPortLabel.objects.get(itmodel=itmodel, order=3)
                return my_network_port_label.name
            else:
                return ''
        except:
            return ''

    def dehydrate_network_port_name_4(self, itmodel):
        try:
            if itmodel.network_ports >= 4:
                my_network_port_label = NetworkPortLabel.objects.get(itmodel=itmodel, order=4)
                return my_network_port_label.name
            else:
                return ''
        except:
            return ''

    class Meta:
        model = ITModel
        exclude = 'id', 'type'
        import_id_fields = ('vendor', 'model_number')
        export_order = ('mount_type', 'vendor', 'model_number', 'height', 'display_color', 'network_ports',
                        'power_ports', 'cpu', 'memory', 'storage', 'comment',
                        'network_port_name_1', 'network_port_name_2', 'network_port_name_3', 'network_port_name_4')
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True

    def before_import_row(self, row, **kwargs):
        if row['mount_type'] == 'asset':
            row['mount_type'] = 'regular'

        if row['mount_type'] == ITModel.Type.BLADE:
            row['height'] = 1
            row['power_ports'] = 0
            row['network_ports'] = 0

    def after_export(self, queryset, data, *args, **kwargs):
        for i, row in enumerate(data):
            del data[i]
            row = list(row)
            if row[0] == "regular":
                row[0] = "asset"
            data.insert(i, row)

    def after_save_instance(self, instance, using_transactions, dry_run):
        my_network_ports = instance.network_ports
        current = [label['name'] for label in instance.networkportlabel_set.order_by('order').values()]
        if len(current) > my_network_ports >= 4:
            raise ValidationError(
                'Cannot decrease amount of network ports.'
            )

        special = []
        for i in range(1, min(5, my_network_ports + 1)):
            try:
                special.append(getattr(instance, 'network_port_name_' + str(i)))
            except:
                special.append('')

        if special != current[:len(special)] or my_network_ports <= 4:
            if instance.asset_set.all().count() > 0:
                raise serializers.ValidationError(
                    "Cannot modify interconnected ITModel attributes while assets are deployed."
                )
            else:
                instance.networkportlabel_set.all().delete()
                create_itmodel_extra(instance, (special + current)[:my_network_ports])


def get_site(row):
    if row:
        if row['datacenter'] and row['rack'] and row['rack_position']:
            return row['datacenter']
        elif row['offline_site']:
            return row['offline_site']
        elif row['chassis_number']:
            chassis = newest_object(
                Asset, ChangePlan.objects.get(id=row['version']), asset_number=row['chassis_number']
            )
            if not chassis:
                raise serializers.ValidationError(
                    "Chassis does not exist."
                )
            return chassis.site
    return None


class AssetResource(VersionedResource):
    class RackForeignKeyWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            if row['datacenter']:
                my_rack = row['rack']
                my_site = get_site(row)
                version = ChangePlan.objects.get(id=row['version'])
                if my_site:
                    site = Site.objects.get(abbr=my_site)
                    rack = newest_object(Rack, version, rack=my_rack, site=site)
                    if not rack:
                        raise serializers.ValidationError(
                            "Rack does not exist."
                        )
                    return add_rack(rack, version)
            return None

        def render(self, value, obj=None):
            return '' if obj and obj.itmodel.type == ITModel.Type.BLADE else super().render(value, obj)

    class ITModelForeignKeyWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            return self.model.objects.get(
                vendor__iexact=row['vendor'],
                model_number__iexact=row['model_number']
            )

    class VersionWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            if value is not None:
                return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
            else:
                return None

    class SiteWidget(ForeignKeyWidget):
        def __init__(self, column, *args, **kwargs):
            self.column = column
            super().__init__(Site, 'abbr', *args, **kwargs)

        def clean(self, value, row=None, *args, **kwargs):
            site = get_site(row)
            return super().clean(site, row, *args, **kwargs)

        def render(self, value, obj=None):
            if value and obj and not obj.itmodel.type == ITModel.Type.BLADE:
                if self.column == 'datacenter' and not value.offline:
                    return value.abbr
                if self.column == 'offline_site' and value.offline:
                    return value.abbr
            return ""

    class ChassisWidget(ForeignKeyWidget):
        def clean(self, value, row=None, *args, **kwargs):
            if value:
                version = ChangePlan.objects.get(id=row['version'])
                chassis = newest_object(Asset, version, asset_number=value)
                return add_asset(chassis, version)
            return None

    datacenter = fields.Field(
        column_name='datacenter',
        attribute='site',
        widget=SiteWidget('datacenter')
    )
    offline_site = fields.Field(
        column_name='offline_site',
        attribute='site',
        widget=SiteWidget('offline_site')
    )
    rack = fields.Field(
        column_name='rack',
        attribute='rack',
        widget=RackForeignKeyWidget(Rack, 'rack')
    )
    vendor = fields.Field(
        column_name='vendor',
        attribute='itmodel',
        widget=ITModelForeignKeyWidget(ITModel, 'vendor')
    )
    model_number = fields.Field(
        column_name='model_number',
        attribute='itmodel',
        widget=ITModelForeignKeyWidget(ITModel, 'model_number')
    )
    owner = fields.Field(
        column_name='owner',
        attribute='owner',
        widget=ForeignKeyWidget(User, 'username')
    )
    power_port_connection_1 = fields.Field(attribute="power_port_connection_1")
    power_port_connection_2 = fields.Field(attribute="power_port_connection_2")
    version = fields.Field(
        attribute='version',
        widget=VersionWidget(ChangePlan, 'id')
    )
    blade_chassis = fields.Field(
        column_name='chassis_number',
        attribute='blade_chassis',
        widget=ChassisWidget(Asset, 'asset_number')
    )
    slot = fields.Field(
        column_name='chassis_slot',
        attribute='slot',
        widget=IntegerWidget()
    )
    display_color = fields.Field(
        column_name='custom_display_color',
        attribute='display_color',
    )
    cpu = fields.Field(
        column_name='custom_cpu',
        attribute='cpu',
    )
    memory = fields.Field(
        column_name='custom_memory',
        attribute='memory',
        widget=IntegerWidget()
    )
    storage = fields.Field(
        column_name='custom_storage',
        attribute='storage',
    )

    def skip_row(self, instance, original):
        try:
            check_asset_perm(self.owner.username, original.site.abbr)
        except:
            pass
        check_asset_perm(self.owner.username, instance.site.abbr)

        port1 = getattr(instance, "power_port_connection_1")
        port2 = getattr(instance, "power_port_connection_2")
        new = [port for port in (port1, port2) if len(port) > 0]
        curr = [port[0] + str(port[1]) for port in instance.powered_set.values_list("pdu__position", "plug_number")]

        if hasattr(original, 'site') and instance.site.abbr != original.site.abbr:
            for port in original.networkport_set.all():
                port.connection = None
                port.save()

        if sorted(new) != sorted(curr):
            return False

        delattr(instance, "power_port_connection_1")
        delattr(instance, "power_port_connection_2")
        return super(AssetResource, self).skip_row(instance, original)

    def dehydrate_power_port_connection_1(self, asset):
        try:
            if asset.itmodel.power_ports >= 1:
                my_powered = Powered.objects.filter(asset=asset, order=1).first()
                if self.version.id != 0 and my_powered is None:
                    my_powered = Powered.objects.filter(
                        asset=versioned_object(asset, ChangePlan.objects.get(id=0), Asset.IDENTITY_FIELDS),
                        order=1
                    ).first()
                if my_powered:
                    return str(my_powered.pdu.position) + str(my_powered.plug_number)
                else:
                    return ''
        except:
            return ''

    def dehydrate_power_port_connection_2(self, asset):
        try:
            if asset.itmodel.power_ports >= 2:
                my_powered = Powered.objects.filter(asset=asset, order=2).first()
                if self.version.id != 0 and my_powered is None:
                    my_powered = Powered.objects.filter(
                        asset=versioned_object(asset, ChangePlan.objects.get(id=0), Asset.IDENTITY_FIELDS),
                        order=2
                    ).first()
                if my_powered:
                    return str(my_powered.pdu.position) + str(my_powered.plug_number)
                else:
                    return ''
        except:
            return ''

    class Meta:
        model = Asset
        exclude = ('id', 'itmodel', 'site', 'commissioned', 'decommissioned_by', 'decommissioned_timestamp')
        import_id_fields = ('asset_number', 'version')
        export_order = ('asset_number', 'hostname', 'datacenter', 'offline_site', 'rack', 'rack_position',
                        'blade_chassis', 'slot', 'vendor', 'model_number',
                        'owner', 'comment', 'power_port_connection_1', 'power_port_connection_2',
                        'display_color', 'cpu', 'memory', 'storage')
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True

    def before_import_row(self, row, **kwargs):
        if row['datacenter']:
            if row['offline_site']:
                raise serializers.ValidationError('You cannot specify both datacenter and offline_site')
        if row['asset_number'] == '':
                max_an = Asset.objects.all().aggregate(Max('asset_number'))
                row['asset_number'] = (max_an['asset_number__max'] or 100000) + 1
        else:
            row['asset_number'] = int(row['asset_number'])

        val = row['custom_display_color']
        row['custom_display_color'] = val if val else None
        val = row['custom_cpu']
        row['custom_cpu'] = val if val else None
        val = row['custom_storage']
        row['custom_storage'] = val if val else None

        row['version'] = self.version.id

    def after_import_row(self, row, row_result, **kwargs):
        if row_result.import_type == 'skip':
            return
        try:
            my_asset = Asset.objects.get(id=row_result.object_id)
        except:
            return  # skip

        my_asset = add_asset(my_asset, self.version)

        if not my_asset.site.offline and not my_asset.itmodel.type == ITModel.Type.BLADE:
            my_rack = my_asset.rack
            special = []
            for i in range(1, min(3, my_asset.itmodel.power_ports + 1)):
                pc = row['power_port_connection_' + str(i)]
                if len(pc) > 0:
                    try:
                        split = re.search(r"\d", pc).start()
                        position = pc[:split]
                        plug = int(pc[split:])
                        special.append({'pdu_id': PDU.objects.get(rack=my_rack, position=position), 'plug': plug})
                    except AttributeError:
                        raise ValidationError('power_port_connection_' + str(i) + " formatted incorrectly")
                    except PDU.DoesNotExist:
                        raise ValidationError(pc + " does not exit on the specified rack")
            current = []
            powered_set = my_asset.powered_set
            if 2 <= len(special) < my_asset.itmodel.power_ports and \
                    powered_set.exists() and powered_set.first().pdu.rack == my_asset.rack:
                special_simple = [port['pdu_id'].position + str(port['plug']) for port in special]

                current = [{'pdu_id': port['pdu'], 'plug': port['plug_number'], 'position': port['pdu__position']}
                           for port in powered_set.order_by('order').values(
                        'pdu', 'plug_number', 'pdu__position')]

                for port in current:
                    simple = port['position'] + str(port['plug'])
                    if simple in special_simple:
                        current.remove(port)

            my_asset.powered_set.all().delete()

            create_ports = False
            net_port = my_asset.networkport_set.first()
            if net_port and net_port.label.itmodel != my_asset.itmodel:
                for port in my_asset.networkport_set.all():
                    port.delete()
                create_ports = True

            if row_result.import_type == "new" or create_ports:
                ports = [{"label": port, "mac_address": None, "connection": None}
                         for port in
                         NetworkPortLabel.objects.filter(itmodel=my_asset.itmodel).values_list('name', flat=True)]
            else:
                ports = None
            my_asset.version = self.version
            create_asset_extra(
                my_asset,
                self.version,
                special + current,
                ports
            )

        if my_asset.itmodel.type == ITModel.Type.BLADE:
            my_asset.rack = my_asset.blade_chassis.rack
            my_asset.save()

        if my_asset.site.offline:
            for port in my_asset.networkport_set.all():
                port.connection = None
                port.save()

    def after_export(self, queryset, data, *args, **kwargs):
        del data['version']
