from django.contrib.auth.models import User
from rest_framework import serializers


def check_asset_perm(username, abbr):
    user = User.objects.get(username=username)
    if user.is_superuser:
        return
    else:
        site_perm = user.permission.site_perm
        if not user.permission.asset_perm or ('Global' not in site_perm and abbr not in site_perm):
            raise serializers.ValidationError("You don't have permission.")
