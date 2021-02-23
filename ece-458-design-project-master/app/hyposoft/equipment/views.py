from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import generics, views
from rest_framework.status import HTTP_200_OK
from hyposoft.utils import generate_racks, add_rack, add_asset, add_network_conn, versioned_object
from .handlers import create_rack_extra, decommission_asset
from .serializers import *
from .models import *
import logging
from hypo_auth.mixins import *
from hypo_auth.handlers import *


class SiteCreate(CreateAndLogMixin, generics.CreateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class ITModelCreate(ITModelPermissionCreateMixin, generics.CreateAPIView):
    queryset = ITModel.objects.all()
    serializer_class = ITModelSerializer


class AssetCreate(AssetPermissionCreateMixin, generics.CreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def create(self, request, *args, **kwargs):
        version = ChangePlan.objects.get(id=get_version(request))
        request.data['power_connections'] = [entry for entry in request.data['power_connections'] if entry]
        if version.id != 0 and request.data['location']['tag'] != 'offline' and request.data['location']['rack']:
            rack = Rack.objects.get(id=request.data['location']['rack'])
            versioned_rack = add_rack(rack, version)
            request.data['location']['rack'] = versioned_rack.id
        return super(AssetCreate, self).create(request, *args, **kwargs)


class RackRangeCreate(views.APIView):
    def post(self, request):
        r1 = request.data['r1']
        r2 = request.data['r2']
        c1 = request.data['c1']
        c2 = request.data['c2']

        racks = generate_racks(r1, r2, c1, c2)

        version = ChangePlan.objects.get(id=get_version(request))
        created = []
        warns = []
        err = []

        for rack in racks:
            try:
                new = Rack(
                    site=Site.objects.get(id=request.data['site']),
                    version=version,
                    rack=rack
                )
                new.save()
                create_rack_extra(new, version)
                created.append(new)
            except IntegrityError:
                warns.append(rack + ' already exists.')
            except Exception as e:
                err.append(str(e))

        return Response({
            'created': [RackSerializer(rack).data for rack in created],
            'warn': warns,
            'err': err
        })


class ITModelUpdate(ITModelPermissionUpdateMixin, generics.UpdateAPIView):
    queryset = ITModel.objects.all()
    serializer_class = ITModelSerializer


class AssetUpdate(AssetPermissionUpdateMixin, generics.UpdateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    @transaction.atomic()
    def update(self, request, *args, **kwargs):  # todo the logic in this looks fishy..
        # Do you need to update data's id or is that done already? what about version?
        # Does the new asset get added to the new version? What about its network ports?
        # Make sure that network ports are not deleted in the offline case but connections are wiped
        version = ChangePlan.objects.get(id=get_version(request))
        asset = self.get_object()
        asset_ver = asset.version
        request.data['power_connections'] = request.data.get('power_connections', [])
        request.data['network_ports'] = request.data.get('network_ports', [])
        request.data['power_connections'] = [entry for entry in request.data['power_connections'] if entry]

        site = Site.objects.get(id=request.data['location']['site'])
        check_asset_perm(request.user.username, site.abbr)
        check_asset_perm(request.user.username, asset.site.abbr)

        if version != asset_ver:
            data = request.data
            if not site.offline:
                rack = versioned_object(asset.rack, version, Rack.IDENTITY_FIELDS)
                if not rack:
                    rack = add_rack(asset.rack, version)
                old_pdus = {port['id']: port['position']
                            for port in asset.rack.pdu_set.order_by('position').values('id', 'position')}
                new_pdus = {port['position']: port['id']
                            for port in rack.pdu_set.order_by('position').values('id', 'position')}
                data['location']['rack'] = rack.id
                for i, port in enumerate(request.data['power_connections']):
                   data['power_connections'][i]['pdu_id'] = new_pdus[old_pdus[int(port['pdu_id'])]]

                for i, port in enumerate(request.data['network_ports']):
                    if port['connection'] is not None:
                        versioned_conn = add_network_conn(NetworkPort.objects.get(id=port['connection']), version)
                        data['network_ports'][i]['connection'] = versioned_conn.id
            else:
                request.data['power_connections'] = []

            if request.data['location']['tag'] == 'chassis-mount':
                chassis = Asset.objects.get(id=request.data['location']['asset'])
                request.data['location']['asset'] = add_asset(chassis, version, Asset.IDENTITY_FIELDS).id
                pass

            serializer = AssetSerializer(data=data, context={'request': request, 'version': version.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=HTTP_200_OK)

        else:
            return super(AssetUpdate, self).update(request, *args, **kwargs)


class SiteUpdate(UpdateAndLogMixin, generics.UpdateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class DestroyWithIdMixin(object):
    def destroy(self, *args, **kwargs):
        id = self.get_object().id
        super().destroy(*args, **kwargs)
        return Response(id, status=status.HTTP_200_OK)


class ITModelDestroy(ITModelPermissionDestroyMixin, ITModelDestroyWithIdMixin, generics.DestroyAPIView):
    queryset = ITModel.objects.all()
    serializer_class = ITModelSerializer

    def delete(self, request, *args, **kwargs):
        if self.get_object().asset_set.all().count() > 0:
            raise serializers.ValidationError(
                "Cannot delete ITModel while assets are deployed."
            )
        return super(ITModelDestroy, self).delete(request, *args, **kwargs)


class VendorList(views.APIView):
    def get(self, request):
        return Response(list(ITModel.objects.values_list('vendor', flat=True).distinct('vendor')))


class AssetDestroy(AssetPermissionDestroyMixin, AssetDestroyWithIdMixin, generics.DestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class RackRangeDestroy(views.APIView):
    def post(self, request):
        r1 = request.data['r1']
        r2 = request.data['r2']
        c1 = request.data['c1']
        c2 = request.data['c2']
        datacenter = request.data['site']

        version = get_version(request)
        removed = []
        warns = []
        err = []

        racks = generate_racks(r1, r2, c1, c2)

        for rackname in racks:
            try:
                rack = Rack.objects.get(rack=rackname, site_id=datacenter, version=version)
                rack_id = rack.id
                rack.delete()
                removed.append(rack_id)
            except Rack.DoesNotExist:
                warns.append(rackname + ' does not exist: rack skipped.')
            except ProtectedError as e:
                decommission = True
                for asset in e.args[1]:
                    if asset.commissioned:
                        decommission = False
                        break
                if decommission:
                    rack.decommissioned = True
                    rack.save()
                    warns.append('Decommissioned assets exist on ' + rackname + ': rack decommissioned.')
                else:
                    err.append('Assets exist on ' + rackname + ': rack skipped.')
            except Exception as e:
                logging.exception(e, exc_info=True)
                err.append('Unexpected error when deleting ' + rackname + '.')

        return Response({
            'removed': removed,
            'warn': warns,
            'err': err
        })


class SiteDestroy(DeleteAndLogMixin, DestroyWithIdMixin, generics.DestroyAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class ITModelRetrieve(generics.RetrieveAPIView):
    queryset = ITModel.objects.all()
    serializer_class = ITModelSerializer


class AssetRetrieve(generics.RetrieveAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class AssetDetailRetrieve(generics.RetrieveAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetDetailSerializer


class RackView(views.APIView):
    def post(self, request):
        rack_ids = request.data['rack_ids']
        racks = [Rack.objects.get(id=id) for id in rack_ids]
        return Response({
            rack.id: {
                "rack": RackSerializer(rack).data,
                "assets": [{"asset": AssetSerializer(asset).data, "model": ITModelSerializer(asset.itmodel).data}
                           for asset in rack.asset_set.order_by('rack_position')]}
            for rack in racks}, status=HTTP_200_OK)


class DecommissionAsset(views.APIView):
    serializer_class = AssetDetailSerializer

    def post(self, request, asset_id):
        if not request.user.is_superuser:
            if not request.user.permission.asset_perm:
                raise serializers.ValidationError("You don't have permission.")
        version = ChangePlan.objects.get(id=get_version(request))
        try:
            asset = decommission_asset(asset_id, self, request.user, version)

            response = DecommissionedAssetSerializer(asset, context={'request': request, 'version': version.id})
            return Response(response.data, status=status.HTTP_202_ACCEPTED)
        except Asset.DoesNotExist:
            raise serializers.ValidationError(
                'Asset does not exist.'
            )
        except ChangePlan.DoesNotExist:
            raise serializers.ValidationError(
                'Change Plan does not exist.'
            )

class AssetIDForAssetNumber(views.APIView):
    def get(self, request, asset_number): 
        asset = Asset.objects.get(asset_number=asset_number, version=0)
        return Response(asset.id)

