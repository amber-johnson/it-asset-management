from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, filters, renderers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from tablib import Dataset
from changeplan.handlers import get_asset, get_power, get_network

import io

from django.db import models, transaction

from equipment.resources import ITModelResource, AssetResource
from equipment.models import ITModel, Asset, Rack
from equipment.filters import ITModelFilter, RackRangeFilter, AssetFilter, RackPositionFilter, HeightFilter
from equipment.serializers import ITModelSerializer, AssetSerializer
from changeplan.models import ChangePlan
from power.models import Powered, PDU
from network.models import NetworkPort
from network.resources import NetworkPortResource

# The Model and Serializer classes are used for compatibility with the browsable API
from hyposoft.utils import get_version, versioned_queryset


class File(models.Model):
    file = models.FileField(blank=False, null=False)


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()


def bool(obj):
    if type(obj) == bool:
        return obj
    return obj == "true" or obj == "True"


def get_errors(result, get_msg):
    return [
        {"row": row.errors[0].row if row.errors else "Row " + str(i), "errors":
            (["Row {} {}: {}".format(i, *item)
              for item in row.validation_error.message_dict.items()])
            if row.validation_error and hasattr(row.validation_error, 'message_dict') else
            (["Row {}: {}".format(i, message)
              for message in row.validation_error.messages]) if row.validation_error
            else [
                get_msg(row, error) for error in row.errors
            ]}
        for i, row in enumerate(result.rows) if len(row.errors) > 0 or row.validation_error is not None
    ]


class ITModelImport(generics.CreateAPIView):
    queryset = ITModel.objects.filter(id=-1)
    serializer_class = FileSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                if not request.user.permission.model_perm:
                    raise serializers.ValidationError("You don't have permission.")
            data = request.data
            force = bool(request.query_params['force'])
            file = data.get('file')
            dataset = Dataset().load(str(file.read(), 'utf-8-sig'), format="csv")
            if not dataset.headers == ['mount_type', 'vendor', 'model_number', 'height', 'display_color',
                                       'network_ports',
                                       'power_ports', 'cpu', 'memory', 'storage', 'comment', 'network_port_name_1',
                                       'network_port_name_2', 'network_port_name_3', 'network_port_name_4']:
                return Response({"status": "error", "errors": [{"errors": "Improperly Formatted CSV"}]}, HTTP_200_OK)

            result = ITModelResource().import_data(dataset, dry_run=not force)

            errors = get_errors(result, lambda row, error: "{} - {}: {}".format(
                row.errors[0].row['vendor'],
                row.errors[0].row['model_number'],
                str(error.error.detail[0]
                    if hasattr(error.error, "detail") and isinstance(error.error.detail, list) else error.error)
            ))

            if len(errors) > 0:
                response = {"status": "error", "errors": errors}
            else:
                response = {
                    "status": "diff" if not force else "success",
                    "diff": {"headers": result.diff_headers, "data": [row.diff for row in result.rows]}}
            return Response(response, HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": "error", "errors":
                            [{"errors": "Unexpected Error! Is your CSV data valid?"}]}, HTTP_200_OK)


class AssetImport(generics.CreateAPIView):
    queryset = Asset.objects.filter(id=-1)
    serializer_class = FileSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                if not request.user.permission.asset_perm:
                    raise serializers.ValidationError("You don't have permission.")
            data = request.data
            force = bool(request.query_params['force'])
            file = data.get('file')
            dataset = Dataset().load(str(file.read(), 'utf-8-sig'), format="csv")
            if not set(dataset.headers) == {'asset_number', 'hostname', 'datacenter', 'offline_site', 'rack',
                                            'rack_position', 'chassis_number', 'chassis_slot', 'vendor', 'model_number',
                                            'owner', 'comment', 'power_port_connection_1', 'power_port_connection_2',
                                            'custom_display_color', 'custom_cpu', 'custom_memory', 'custom_storage'}:
                return Response({"status": "error", "errors": [{"errors": "Improperly Formatted CSV"}]}, HTTP_200_OK)

            result = AssetResource(
                get_version(request), request.user, True).import_data(dataset, dry_run=not force)

            errors = get_errors(result, lambda row, error: "{} {}: {}".format(
                row.errors[0].row['asset_number'],
                row.errors[0].row['hostname'],
                str(error.error.detail[0]
                    if hasattr(error.error, "detail") and isinstance(error.error.detail, list) else error.error)
            ))

            if len(errors) > 0:
                return Response({"status": "error", "errors": errors}, HTTP_200_OK)
            elif not force:
                resource = AssetResource(get_version(request), request.user, False)
                result = resource.import_data(dataset)

                errors = get_errors(result, lambda row, error: "{} {}: {}".format(
                    row.errors[0].row['asset_number'],
                    row.errors[0].row['hostname'],
                    str(error.error.detail[0]
                        if hasattr(error.error, "detail") and isinstance(error.error.detail, list) else error.error)
                ))

                if len(errors) > 0:
                    return Response({"status": "error", "errors": errors}, HTTP_200_OK)

                try:
                    changeplan = ChangePlan.objects.get(owner=request.user, name="_BULK_IMPORT_" + str(id(resource)))
                except ChangePlan.DoesNotExist:
                    return Response({"status": "diff", "asset": ["No Changes"], "power": []}, status=HTTP_200_OK)

                live = ChangePlan.objects.get(id=0)
                asset_messages = []
                power_messages = []

                asset_diff = get_asset(changeplan, live)
                power_diff = get_power(changeplan, live)

                for diff in asset_diff:
                    if diff['live']:
                        asset_messages += ["#{}: {}".format(diff['live'].asset_number, message) for message in
                                           diff['messages']]
                    else:
                        asset_messages += ['{}: {}'.format(diff['new'].hostname, message) for message in
                                           diff['messages']]

                for diff in power_diff:
                    if diff['live']:
                        power_messages += ["#{}: {}".format(diff['live'].asset.asset_number, message) for message in
                                           diff['messages']]
                    else:
                        power_messages += [
                            "#{}: {}".format(diff['new'].asset.asset_number or diff['new'].asset, message)
                            for message in diff['messages']]

                response = {
                    'status': "diff",
                    'asset': asset_messages,
                    'power': power_messages,
                }

                for model in (Powered, NetworkPort, Asset, PDU, Rack):
                    if model == Asset:
                        model.objects.filter(version=changeplan, itmodel__type=ITModel.Type.BLADE).delete()
                    model.objects.filter(version=changeplan).delete()
                changeplan.delete()

                return Response(response, status=HTTP_200_OK)

            else:
                return Response({}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": "error", "errors":
                            [{"errors": "Unexpected Error! Is your CSV data valid?"}]}, HTTP_200_OK)


class NetworkImport(generics.CreateAPIView):
    queryset = NetworkPort.objects.filter(id=-1)
    serializer_class = FileSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                if not request.user.permission.asset_perm:
                    raise serializers.ValidationError("You don't have permission.")
            data = request.data
            force = bool(request.query_params['force'])
            file = data.get('file')
            dataset = Dataset().load(str(file.read(), 'utf-8-sig'), format="csv")
            if not dataset.headers == ['src_hostname', 'src_port', 'src_mac', 'dest_hostname', 'dest_port']:
                return Response({"status": "error", "errors": [{"errors": "Improperly Formatted CSV"}]}, HTTP_200_OK)
            result = NetworkPortResource(
                get_version(request), request.user, True).import_data(dataset, dry_run=not force)

            errors = get_errors(result, lambda row, error: "{} -> {}: {}".format(
                row.errors[0].row['src_hostname'],
                row.errors[0].row['dest_hostname'],
                str(error.error.detail[0]
                    if hasattr(error.error, "detail") and isinstance(error.error.detail, list) else error.error)
            ))

            if len(errors) > 0:
                return Response({"status": "error", "errors": errors}, HTTP_200_OK)
            elif not force:
                resource = NetworkPortResource(get_version(request), request.user, False)
                result = resource.import_data(dataset)

                errors = get_errors(result, lambda row, error: "{} -> {}: {}".format(
                    row.errors[0].row['src_hostname'],
                    row.errors[0].row['dest_hostname'],
                    str(error.error.detail[0]
                        if hasattr(error.error, "detail") and isinstance(error.error.detail, list) else error.error)
                ))

                if len(errors) > 0:
                    return Response({"status": "error", "errors": errors}, HTTP_200_OK)

                try:
                    changeplan = ChangePlan.objects.get(owner=request.user, name="_BULK_IMPORT_" + str(id(resource)))
                except ChangePlan.DoesNotExist:
                    return Response({"status": "skip"}, status=HTTP_200_OK)

                live = ChangePlan.objects.get(id=0)
                messages = []

                network_diff = get_network(changeplan, live)

                for diff in network_diff:
                    if diff['live']:
                        messages += ["#{} – {}: {}".format(
                            diff['live'].asset.hostname, diff['live'].label.name, message) for message in diff['messages']]
                    else:
                        messages += ["#{} – {}: {}".format(
                            diff['live'].asset.hostname, diff['new'].label.name, message) for message in diff['messages']]

                response = {
                    'status': "diff",
                    'network': messages,
                }

                for model in (Powered, NetworkPort, Asset, PDU, Rack):
                    if model == Asset:
                        model.objects.filter(version=changeplan, itmodel__type=ITModel.Type.BLADE).delete()
                    model.objects.filter(version=changeplan).delete()
                changeplan.delete()

                return Response(response, status=HTTP_200_OK)

            else:
                return Response({}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": "error", "errors":
                            [{"errors": "Unexpected Error! Is your CSV data valid?"}]}, HTTP_200_OK)


class CSVRenderer(renderers.BaseRenderer):
    media_type = "application/octet-stream"
    format = "txt"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data.export('csv')


class ITModelExport(generics.ListAPIView):
    renderer_classes = [CSVRenderer]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend, HeightFilter]
    search_fields = [
        'vendor',
        'model_number',
        'cpu',
        'storage',
        'comment'
    ]

    queryset = ITModel.objects.all()
    serializer_class = ITModelSerializer
    filterset_class = ITModelFilter

    def get(self, request, *args, **kwargs):
        data = ITModelResource().export(queryset=self.filter_queryset(self.get_queryset()))
        return Response(data, HTTP_200_OK)


class AssetExport(generics.ListAPIView):
    renderer_classes = [CSVRenderer]

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
        RackRangeFilter,
        RackPositionFilter,
    ]
    search_fields = [
        'itmodel__vendor',
        'itmodel__model_number',
        'hostname',
        'owner__username',
        'owner__first_name',
        'owner__last_name',
        'asset_number'
    ]

    def get_queryset(self):
        combined = Asset.objects.filter(commissioned=Asset.Decommissioned.COMMISSIONED)
        version = ChangePlan.objects.get(id=get_version(self.request))
        versioned = versioned_queryset(combined, version, Asset.IDENTITY_FIELDS)
        return versioned

    serializer_class = AssetSerializer
    filterset_class = AssetFilter

    def get(self, request, *args, **kwargs):
        data = AssetResource(get_version(request), request.user) \
            .export(queryset=self.filter_queryset(self.get_queryset()))
        return Response(data, HTTP_200_OK)


class NetworkExport(generics.ListAPIView):
    renderer_classes = [CSVRenderer]

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
        RackRangeFilter,
        RackPositionFilter
    ]
    search_fields = [
        'itmodel__vendor',
        'itmodel__model_number',
        'hostname',
        'owner__username',
        'owner__first_name',
        'owner__last_name',
        'asset_number'
    ]

    def get_queryset(self):
        return NetworkPort.objects.filter(asset__commissioned=Asset.Decommissioned.COMMISSIONED)

    serializer_class = AssetSerializer
    filterset_class = AssetFilter

    def get(self, request, *args, **kwargs):
        data = NetworkPortResource(get_version(request), request.user).export(version_id=get_version(request))
        return Response(data, HTTP_200_OK)
