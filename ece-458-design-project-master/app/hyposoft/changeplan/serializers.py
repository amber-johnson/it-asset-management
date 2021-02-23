import datetime

from rest_framework import serializers

from equipment.serializers import AssetDetailSerializer
from .handlers import get_asset, get_power, get_network
from .models import ChangePlan


class ChangePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePlan
        fields = ['id', 'name', 'executed_at']

    def to_internal_value(self, data):
        data = super(ChangePlanSerializer, self).to_internal_value(data)
        data['owner'] = self.context['request'].user
        return data

    def to_representation(self, instance):
        data = super(ChangePlanSerializer, self).to_representation(instance)
        old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        new_format = '%d-%m-%Y %H:%M:%S'

        if data['executed_at'] is not None:
            data['executed_at'] = datetime.datetime.strptime(data['executed_at'], old_format).strftime(new_format) + ' UTC'
        return data


class ChangePlanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePlan
        fields = ['id', 'name', 'executed_at']

    def to_representation(self, instance):
        data = super(ChangePlanDetailSerializer, self).to_representation(instance)
        live = ChangePlan.objects.get(id=0)
        diffs = []
        assetDiff = get_asset(instance, live)
        powerDiff = get_power(instance, live)
        networkDiff = get_network(instance, live)

        for diff in assetDiff:
            entry = {}
            asset = diff['new']
            entry['live'] = AssetDetailSerializer(diff['live']).data if diff['live'] else None
            entry['cp'] = AssetDetailSerializer(asset).data

            conflicts = diff['conflicts']

            for power in powerDiff:
                if power['new'] and power['new'].asset == asset:
                    conflicts += power['conflicts']

            for network in networkDiff:
                if network['new'] and network['new'].asset == asset:
                    conflicts += network['conflicts']

            entry['conflicts'] = conflicts
            if diff['messages'] or conflicts:
                diffs.append(entry)

        data['diffs'] = diffs

        old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        new_format = '%d-%m-%Y %H:%M:%S'

        if data['executed_at'] is not None:
            data['executed_at'] = datetime.datetime.strptime(data['executed_at'], old_format).strftime(new_format) + ' UTC'
        return data
