from rest_framework import serializers

from .handlers import check_asset_perm
from system_log.views import CreateAndLogMixin, UpdateAndLogMixin, DeleteAndLogMixin
from rest_framework.response import Response
from rest_framework import status
from equipment.models import Site


class ITModelPermissionCreateMixin(CreateAndLogMixin):
    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            super(ITModelPermissionCreateMixin, self).perform_create(serializer)
            return
        elif not self.request.user.permission.model_perm:
            raise serializers.ValidationError("You don't have permission.")
        else:
            super(ITModelPermissionCreateMixin, self).perform_create(serializer)


class ITModelPermissionUpdateMixin(UpdateAndLogMixin):
    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            super(ITModelPermissionUpdateMixin, self).perform_update(serializer)
            return
        elif not self.request.user.permission.model_perm:
            raise serializers.ValidationError("You don't have permission.")
        else:
            super(ITModelPermissionUpdateMixin, self).perform_update(serializer)


class ITModelPermissionDestroyMixin(DeleteAndLogMixin):
    def perform_destroy(self, instance):
        if self.request.user.is_superuser:
            super(ITModelPermissionDestroyMixin, self).perform_destroy(instance)
            return
        if not self.request.user.permission.model_perm:
            raise serializers.ValidationError("You don't have permission.")
        else:
            super(ITModelPermissionDestroyMixin, self).perform_destroy(instance)


class ITModelDestroyWithIdMixin(object):
    def destroy(self, *args, **kwargs):
        if self.request.user.is_superuser:
            id = self.get_object().id
            super().destroy(*args, **kwargs)
            return Response(id, status=status.HTTP_200_OK)
        if not self.request.user.permission.model_perm:
            raise serializers.ValidationError("You don't have permission.")
        else:
            id = self.get_object().id
            super().destroy(*args, **kwargs)
            return Response(id, status=status.HTTP_200_OK)


class AssetPermissionCreateMixin(CreateAndLogMixin):
    def perform_create(self, serializer):
        check_asset_perm(self.request.user.username, serializer.validated_data['site'].abbr)
        return super(AssetPermissionCreateMixin, self).perform_create(serializer)


class AssetPermissionUpdateMixin(UpdateAndLogMixin):
    def perform_update(self, serializer):
        check_asset_perm(self.request.user.username, self.get_object().site.abbr)
        check_asset_perm(self.request.user.username, serializer.validated_data['site'].abbr)
        return super(AssetPermissionUpdateMixin, self).perform_update(serializer)


class AssetPermissionDestroyMixin(DeleteAndLogMixin):
    def perform_destroy(self, instance):
        abbr = instance.site.abbr
        if self.request.user.is_superuser:
            super(AssetPermissionDestroyMixin, self).perform_destroy(instance)
            return
        else:
            site_perm = self.request.user.permission.site_perm
            if not self.request.user.permission.asset_perm or ('Global' not in site_perm and abbr not in site_perm):
                raise serializers.ValidationError("You don't have permission.")
        super(AssetPermissionDestroyMixin, self).perform_destroy(instance)


class AssetDestroyWithIdMixin(object):
    def destroy(self, *args, **kwargs):
        abbr = self.get_object().site.abbr
        if self.request.user.is_superuser:
            id = self.get_object().id
            super().destroy(*args, **kwargs)
            return Response(id, status=status.HTTP_200_OK)
        else:
            site_perm = self.request.user.permission.site_perm
            if not self.request.user.permission.asset_perm or ('Global' not in site_perm and abbr not in site_perm):
                raise serializers.ValidationError("You don't have permission.")
        id = self.get_object().id
        super().destroy(*args, **kwargs)
        return Response(id, status=status.HTTP_200_OK)
