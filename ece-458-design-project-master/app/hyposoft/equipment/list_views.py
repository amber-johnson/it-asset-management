from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import dateparse
from rest_framework import filters, generics, serializers
from rest_framework.pagination import PageNumberPagination
from hyposoft.utils import get_version, versioned_queryset, get_site
from .serializers import ITModelEntrySerializer, AssetEntrySerializer, DecommissionedAssetSerializer, \
    AssetSerializer, RackSerializer, SiteSerializer, ITModelPickSerializer
from .filters import ITModelFilter, AssetFilter, RackRangeFilter, ChangePlanFilter, RackPositionFilter, HeightFilter
from .models import *


# Filters the Rack and Asset ListAPIViews based on the site in the request
class FilterBySiteMixin(object):
    def get_queryset(self):
        site = get_site(self.request)
        model = self.get_serializer_class().Meta.model
        queryset = model.objects.all()
        if site is not None:
            if not Site.objects.filter(id=site).exists():
                raise serializers.ValidationError("Site does not exist")
            return queryset.filter(site__id=site)
        return queryset


class PageSizePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class ITModelList(generics.ListAPIView):
    """
    Class for returning ITModels after filtering criteria.
    """

    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter, HeightFilter]
    search_fields = [
        'vendor',
        'model_number',
        'cpu',
        'storage',
        'comment',
        'type'
    ]
    ordering_fields = [
        'id',
        'vendor',
        'model_number',
        'height',
        'display_color',
        'power_ports',
        'network_ports',
        'cpu',
        'memory',
        'storage',
        'type'
    ]
    ordering = 'id'

    queryset = ITModel.objects.all()
    serializer_class = ITModelEntrySerializer
    filterset_class = ITModelFilter
    pagination_class = PageSizePagination


class ITModelPickList(generics.ListAPIView):
    queryset = ITModel.objects.all()
    serializer_class = ITModelPickSerializer


class AssetList(FilterBySiteMixin, generics.ListAPIView):
    """
    Class for returning Assets after filtering criteria.
    """

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
        RackRangeFilter,
        RackPositionFilter,
        ChangePlanFilter
    ]
    search_fields = [
        'itmodel__vendor',
        'itmodel__model_number',
        'itmodel__type',
        'hostname',
        'networkport__mac_address',
        'owner__username',
        'owner__first_name',
        'owner__last_name',
        'asset_number',
    ]
    ordering_fields = [
        'id',
        'asset_number',
        'itmodel__vendor',
        'itmodel__model_number',
        'hostname',
        'site__abbr',
        'rack__rack',
        'rack_position',
        'owner'
    ]

    def get_queryset(self):
        return super(AssetList, self).get_queryset().filter(commissioned=Asset.Decommissioned.COMMISSIONED).order_by(
            'asset_number', 'itmodel__vendor', 'itmodel__model_number')

    serializer_class = AssetEntrySerializer
    filterset_class = AssetFilter
    pagination_class = PageSizePagination


class AssetPickList(generics.ListAPIView):
    def get_queryset(self):
        version = ChangePlan.objects.get(id=get_version(self.request))
        queryset = Asset.objects.all()
        datacenter_id = self.request.query_params.get('site_id', None)
        if datacenter_id is not None:
            queryset = queryset.filter(site_id=datacenter_id)
        rack_id = self.request.query_params.get('rack_id', None)
        if rack_id is not None:
            rack = Rack.objects.filter(id=rack_id).first()
            if rack is not None:
                queryset = queryset.filter(rack__rack=rack.rack)
        if 'asset_id' in self.request.query_params:
            queryset = queryset.exclude(id=self.request.query_params['asset_id'])
        queryset = versioned_queryset(queryset, version, Asset.IDENTITY_FIELDS)
        return queryset

    serializer_class = AssetSerializer
    filter_backends = [ChangePlanFilter]


class DecommissionedAssetList(generics.ListAPIView):
    filter_backends = [
        filters.OrderingFilter
    ]

    ordering_fields = [
        'id',
        'itmodel__vendor',
        'itmodel__model_number',
        'hostname',
        'site__abbr',
        'rack__rack',
        'rack_position',
        'owner',
        'decommissioned_by',
        'decommissioned_timestamp'
    ]
    ordering = 'id'

    def get_queryset(self):
        queryset = Asset.objects.filter(commissioned=None)
        user = self.request.query_params.get('username', None)
        time_from = self.request.query_params.get('timestamp_from', None)
        time_to = self.request.query_params.get('timestamp_to', None)
        decommissioned_by = self.request.query_params.get('decommissioned_by', None)
        site = get_site(self.request)
        version = get_version(self.request)

        if site:
            queryset = queryset.filter(site__id=site)

        if user:
            queryset = queryset.filter(owner__username=user)

        if time_from and time_to:
            dt_from = dateparse.parse_datetime(time_from)
            dt_to = dateparse.parse_datetime(time_to)

            queryset = queryset.filter(decommissioned_timestamp__range=(dt_from, dt_to))

        if decommissioned_by:
            queryset = queryset.filter(
                Q(decommissioned_by__username__icontains=decommissioned_by) |
                Q(decommissioned_by__first_name__icontains=decommissioned_by) |
                Q(decommissioned_by__last_name__icontains=decommissioned_by)
            )

        queryset = queryset.filter(version__parent_id__in=(0, version))

        return queryset

    serializer_class = DecommissionedAssetSerializer
    pagination_class = PageSizePagination


class RackList(FilterBySiteMixin, generics.ListAPIView):
    queryset = Rack.objects.all()
    serializer_class = RackSerializer
    filter_backends = [ChangePlanFilter]


class SiteList(generics.ListAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
