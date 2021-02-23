import datetime

from django.db import transaction
from django.db.models import Max

from network.handlers import net_graph
from hyposoft.utils import get_version, versioned_queryset
from network.serializers import NetworkPortSerializer
from .handlers import create_asset_extra, create_itmodel_extra
from .models import *
from network.models import NetworkPort, NetworkPortLabel
from power.models import PDU, Powered
from power.handlers import update_asset_power, is_blade_power_on

from rest_framework import serializers
from hyposoft.users import UserSerializer


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'abbr', 'name', 'offline']

    def to_internal_value(self, data):
        site_type = data.pop('type', None)
        if site_type is not None:
            data['offline'] = site_type == 'offline-storage'
        return super(SiteSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        data = super(SiteSerializer, self).to_representation(instance)
        data['type'] = 'offline-storage' if data.pop('offline') else 'datacenter'
        return data

    @transaction.atomic()
    def update(self, instance, validated_data):
        if hasattr(instance, 'type'):
            if instance.type == 'offline-storage' and validated_data['type'] == 'datacenter':
                raise serializers.ValidationError(
                    "Cannot transform an offline site into a datacenter."
                )
            elif instance.type == 'datacenter' and validated_data['type'] == 'offline-storage':
                instance.asset_set.update(rack=None, rack_position=None)
                return super(SiteSerializer, self).update(instance, validated_data)
        return super(SiteSerializer, self).update(instance, validated_data)


class ITModelEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ITModel
        exclude = ['comment']


class ITModelSerializer(serializers.ModelSerializer):
    network_port_labels = serializers.ListField(
        child=serializers.CharField(
            allow_blank=True
        ),
        # Without the following line, Django will raise an error when
        # attempting to read the field from the database
        # (it doesn't exist there)
        required=False
    )

    class Meta:
        model = ITModel
        # using __all__ syntax is required to bypass check that would
        # otherwise throw error for network_port_labels
        fields = "__all__"

    def to_internal_value(self, data):

        labels = data.get('network_port_labels')
        if labels is None:
            if not self.partial:
                data['network_ports'] = 0
            return super(ITModelSerializer, self).to_internal_value(data)
        if not isinstance(labels, list):
            raise serializers.ValidationError({
                'network_port_labels': 'This field must be a list.'
            })
        data['network_ports'] = len(labels)

        return super(ITModelSerializer, self).to_internal_value(data)

    @transaction.atomic()
    def create(self, validated_data):
        if validated_data['type'] == ITModel.Type.BLADE:
            validated_data['height'] = 0
            validated_data['power_ports'] = 0
            validated_data['network_port_labels'] = []

        labels = validated_data.pop('network_port_labels')

        # Validate the new model and save it to the database
        itmodel = super(ITModelSerializer, self).create(validated_data)

        # At this point, model has been validated and created
        if labels:
            create_itmodel_extra(itmodel, labels)

        return itmodel

    @transaction.atomic()
    def update(self, instance, validated_data):
        if instance.type != validated_data['type']:
            raise serializers.ValidationError(
                "You cannot change the type of a Model."
            )
        ports = instance.networkportlabel_set.all()
        old_ports = [name for name in ports.values_list('name', flat=True).order_by('order')]
        new_ports = validated_data['network_port_labels']
        if instance.asset_set.exists():
            def throw():
                raise serializers.ValidationError(
                    "Cannot modify interconnected ITModel attributes while assets are deployed."
                )

            if instance.height != validated_data['height']:
                throw()
            if instance.power_ports != validated_data['power_ports']:
                throw()
            if old_ports != new_ports:
                throw()
        elif old_ports != new_ports:
            NetworkPortLabel.objects.filter(itmodel=instance).delete()
            create_itmodel_extra(instance, validated_data['network_port_labels'])

        return super(ITModelSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        data = super(ITModelSerializer, self).to_representation(instance)
        ports = NetworkPortLabel.objects.filter(itmodel=instance)
        data['network_port_labels'] = [name for name in ports.values_list('name', flat=True).order_by('order')]

        return data

    def validate_network_port_labels(self, value):
        has_digits = False
        has_blanks = False

        for label in value:
            if label.isdigit():
                has_digits = True
            if len(label) == 0:
                has_blanks = True
            if has_digits and has_blanks:
                raise serializers.ValidationError(
                    "If integer label names are used, all label names must be specified."
                )

        # This ensures that the response to the API call is correct
        # The logic is duplicated in handers.py for bulk import
        # It may not be necessary there depending on how that ends up being implemented
        for i in range(1, len(value) + 1):
            if len(value[i - 1]) == 0:
                value[i - 1] = str(i)

        return value


class ITModelPickSerializer(serializers.ModelSerializer):
    class Meta:
        model = ITModel
        fields = ['id']

    def to_representation(self, instance):
        return {'id': instance.id, 'str': str(instance)}


class AssetEntrySerializer(serializers.ModelSerializer):
    model = serializers.CharField(source='itmodel')
    owner = serializers.CharField()

    class Meta:
        model = Asset
        fields = [
            'id',
            'itmodel',
            'model',
            'asset_number',
            'hostname',
            'owner',
        ]

    def to_representation(self, instance):
        data = super(AssetEntrySerializer, self).to_representation(instance)

        if instance.slot is not None:
            data['location'] = "Chassis {}: Slot {}".format(instance.blade_chassis, instance.slot)
        elif instance.site.offline:
            data['location'] = instance.site.abbr
        else:
            data['location'] = "{}: Rack {}U{}".format(instance.site.abbr, instance.rack.rack, instance.rack_position)

        update_asset_power(instance)
        networked = False
        for pdu in instance.pdu_set.all():
            if pdu.networked:
                networked = True
                break
    
        if not instance.site.offline:
            if instance.itmodel.type == ITModel.Type.BLADE:
                vendor_bmi = instance.blade_chassis.itmodel.vendor == "BMI"
                valid_hostname = len(instance.blade_chassis.hostname or "") != 0
                data['power_action_visible'] = vendor_bmi and valid_hostname
            else: 
                data['power_action_visible'] = networked and instance.commissioned is not None and instance.version.id == 0
        else:
            data['power_action_visible'] = False
        return data


class AssetSerializer(serializers.ModelSerializer):
    class PowerConnSerializer(serializers.Serializer):
        pdu_id = serializers.PrimaryKeyRelatedField(
            queryset=PDU.objects.all()
        )
        plug = serializers.IntegerField()

    power_connections = PowerConnSerializer(required=False, many=True)

    class NetPortSerializer(serializers.Serializer):
        label = serializers.CharField()
        mac_address = serializers.CharField(
            allow_null=True
        )
        connection = serializers.PrimaryKeyRelatedField(
            queryset=NetworkPort.objects.all(),
            allow_null=True
        )

    network_ports = NetPortSerializer(required=False, many=True)

    asset_number = serializers.IntegerField(
        allow_null=True
    )

    class Meta:
        model = Asset
        exclude = ['commissioned', 'decommissioned_by', 'decommissioned_timestamp']

    def to_internal_value(self, data):
        req = self.context['request']
        # Value of 0 represents live, and is the default
        version = get_version(req)
        data['version'] = self.context.get('version') or version

        location = data.pop('location')
        data['site'] = location['site']
        if location['tag'] == 'rack-mount':
            data['rack'] = location['rack']
            # data['rack_position'] = location['position'] ???
            data['rack_position'] = location['rack_position']
        elif location['tag'] == 'chassis-mount':
            data['blade_chassis'] = location['asset']
            data['slot'] = location['slot']
            data['rack'] = location['rack']
            data['rack_position'] = None
        elif location['tag'] == 'offline':
            data['rack'] = None
            data['rack_position'] = None
        else:
            raise serializers.ValidationError(
                "Invalid location given for this asset."
            )

        return super(AssetSerializer, self).to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data):
        power_connections = validated_data.pop('power_connections')
        net_ports = validated_data.pop('network_ports')

        # Validate the new asset and save it to the database
        asset = super(AssetSerializer, self).create(validated_data)

        # At this point, asset has been validated and created
        create_asset_extra(asset, validated_data['version'], power_connections, net_ports)

        return asset

    @transaction.atomic()
    def update(self, instance, validated_data):
        power_connections = validated_data.pop('power_connections', None)
        net_ports = validated_data.pop('network_ports', None)

        if power_connections:
            Powered.objects.filter(asset=instance).delete()
        if net_ports or validated_data['itmodel'] != instance.itmodel:
            NetworkPort.objects.filter(asset=instance).delete()

        instance = super(AssetSerializer, self).update(instance, validated_data)
        create_asset_extra(instance, validated_data['version'], power_connections, net_ports)

        instance.blade_set.update(rack=instance.rack, site=instance.site)

        return instance

    def to_representation(self, instance):
        data = super(AssetSerializer, self).to_representation(instance)
        if not instance.site.offline and not instance.itmodel.type == ITModel.Type.BLADE:
            connections = Powered.objects.filter(asset=instance)
            ports = NetworkPort.objects.filter(asset=instance)
            if instance.version.id != 0:
                connections = versioned_queryset(connections, instance.version, Powered.IDENTITY_FIELDS)
                ports = versioned_queryset(ports, instance.version, NetworkPort.IDENTITY_FIELDS)
            data['power_connections'] = [
                {'pdu_id': conn['pdu'], 'plug': conn['plug_number']} for conn in
                connections.values('pdu', 'plug_number')]
            data['network_ports'] = [
                NetworkPortSerializer(port).data
                for port in ports.order_by('label') if port
            ]
            update_asset_power(instance)
            networked = instance.pdu_set.filter(networked=True)
            if networked.exists() and instance.version.id == 0:
                data['power_state'] = "Off"
                for pdu in networked:
                    if pdu.powered_set.filter(asset=instance, on=True).exists():
                        data['power_state'] = "On"
                        break
            else:
                data['power_state'] = None
        elif not instance.site.offline and instance.itmodel.type == ITModel.Type.BLADE:
            chassis_hostname = instance.blade_chassis.hostname
            vendor_bmi = instance.blade_chassis.itmodel.vendor == "BMI"
            if chassis_hostname and vendor_bmi:
                data['power_state'] = "On" if is_blade_power_on(chassis_hostname, instance.slot) else "Off"
            else:
                data['power_state'] = None
        else:
            data['power_connections'] = []
            data['network_ports'] = []
            data['power_state'] = None

        data['decommissioned'] = not instance.commissioned
        data['network_graph'] = net_graph(instance.id)

        location = {"site": instance.site.id}
        if instance.rack_position is not None:
            location['tag'] = 'rack-mount'
            location['rack'] = instance.rack.id
            location['rack_position'] = instance.rack_position
        elif instance.slot is not None:
            location['tag'] = 'chassis-mount'
            location['rack'] = instance.blade_chassis.rack.id if instance.blade_chassis.rack else None
            location['asset'] = instance.blade_chassis.id
            location['slot'] = instance.slot
        elif instance.site.offline:
            location['tag'] = 'offline'
        else:
            raise serializers.ValidationError(
                "Location of this asset is inconsistent."
            )
        data['location'] = location

        del data['site']
        del data['rack']
        del data['rack_position']
        del data['blade_chassis']
        del data['slot']

        return data

    def validate_asset_number(self, value):
        if value is None and get_version(self.context['request']) == 0:
            max_an = Asset.objects.all().aggregate(Max('asset_number'))
            asset_number = (max_an['asset_number__max'] or 100000) + 1
            return asset_number

        return value

    def validate_hostname(self, value):
        return None if value == "" else value


class RackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rack
        fields = ["id", "rack", "site", "decommissioned"]


class AssetDetailSerializer(AssetSerializer):
    itmodel = ITModelSerializer()
    site = SiteSerializer()
    rack = RackSerializer()
    decommissioned_by = UserSerializer()
    owner = UserSerializer()

    class Meta:
        model = Asset
        exclude = ['commissioned']

    def to_representation(self, instance):
        data = super(AssetDetailSerializer, self).to_representation(instance)

        for i, connection in enumerate(data.get('power_connections') or []):
            pdu = PDU.objects.get(id=connection['pdu_id'])
            data['power_connections'][i]['label'] = pdu.position + str(connection['plug'])
        for i, port in enumerate(data.get('network_ports') or []):
            if port['connection']:
                data['network_ports'][i]['connection_str'] = str(NetworkPort.objects.get(id=port['connection']))

        data['location']['site'] = SiteSerializer(Site.objects.get(id=data['location']['site'])).data
        if data['location']['tag'] == 'rack-mount':
            data['location']['rack'] = RackSerializer(Rack.objects.get(id=data['location']['rack'])).data
        if data['location']['tag'] == 'chassis-mount':
            if data['location']['rack']:
                data['location']['rack'] = RackSerializer(Rack.objects.get(id=data['location']['rack'])).data
            data['location']['asset'] = AssetSerializer(Asset.objects.get(id=data['location']['asset'])).data

        old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        new_format = '%m-%d-%Y %H:%M:%S'

        if data['decommissioned_timestamp']:
            data['decommissioned_timestamp'] = \
                datetime.datetime.strptime(data['decommissioned_timestamp'], old_format).strftime(new_format) + ' UTC'

        return data


class DecommissionedAssetSerializer(AssetEntrySerializer):
    itmodel = serializers.StringRelatedField()
    decommissioned_by = serializers.StringRelatedField()

    class Meta:
        model = Asset
        fields = [
            'id',
            'itmodel',
            'hostname',
            'owner',
            'rack',
            'rack_position',
            'decommissioned_by',
            'decommissioned_timestamp'
        ]

    def to_representation(self, instance):
        data = super(DecommissionedAssetSerializer, self).to_representation(instance)
        old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        new_format = '%m-%d-%Y %H:%M:%S'

        if data['decommissioned_timestamp']:
            data['decommissioned_timestamp'] = \
                datetime.datetime.strptime(data['decommissioned_timestamp'], old_format).strftime(new_format) + ' UTC'
        return data
