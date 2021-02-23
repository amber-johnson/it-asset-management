from rest_framework import serializers

from .models import NetworkPortLabel, NetworkPort


class NetworkPortLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkPortLabel
        fields = '__all__'


class NetworkPortSerializer(serializers.ModelSerializer):
    asset_str = serializers.StringRelatedField(source="asset")
    label = serializers.StringRelatedField(source="label.name")

    class Meta:
        model = NetworkPort
        fields = ['id', 'asset_str', 'label', 'mac_address', 'connection']
