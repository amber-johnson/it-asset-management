import datetime
from rest_framework import serializers
from .models import ActionLog


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionLog
        fields = '__all__'

    def to_representation(self, instance):
        data = super(LogSerializer, self).to_representation(instance)
        old_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        new_format = '%d-%m-%Y %H:%M:%S'

        data['timestamp'] = datetime.datetime.strptime(data['timestamp'], old_format).strftime(new_format) + ' UTC'
        return data
