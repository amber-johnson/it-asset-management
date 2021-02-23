from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Permission


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Incorrect email or password.')

        return {'user': user}


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['model_perm', 'asset_perm', 'power_perm', 'audit_perm', 'admin_perm', 'site_perm']


class UserPermSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'permission']

    def update(self, instance, validated_data):
        perm = validated_data.pop('permission')
        obj = Permission.objects.get(user=instance)
        for (field, val) in perm.items():
            setattr(obj, field, val)
        obj.save()
        return super(UserPermSerializer, self).update(instance, validated_data)
