from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend

from changeplan.models import ChangePlan
from .models import ITModel, Asset
from hyposoft.utils import generate_racks, get_version, versioned_queryset


class HeightFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        height_min = request.query_params.get('height_min')
        height_max = request.query_params.get('height_max')
        if height_min == '1' and height_max == '42':
            return queryset

        return queryset.filter(
            height__range=(height_min, height_max), type__in=(ITModel.Type.REGULAR, ITModel.Type.CHASSIS))


class ITModelFilter(filters.FilterSet):
    network_ports = filters.RangeFilter()
    power_ports = filters.RangeFilter()
    memory = filters.RangeFilter()

    class Meta:
        model = ITModel
        fields = ['network_ports', 'power_ports', 'memory', 'type']


class RackRangeFilter(BaseFilterBackend):
    template = 'rest_framework/filters/search.html'

    def filter_queryset(self, request, queryset, view):
        r1 = request.query_params.get('r1')
        r2 = request.query_params.get('r2')
        c1 = request.query_params.get('c1')
        c2 = request.query_params.get('c2')

        if r1 and r2 and c1 and c2:
            return queryset.filter(
                rack__rack__in=generate_racks(r1, r2, c1, c2)
            )
        else:
            return queryset


class RackPositionFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        pos_min = request.query_params.get('rack_position_min')
        pos_max = request.query_params.get('rack_position_max')

        if pos_min and pos_max:
            return queryset.filter(Q(rack_position__range=(pos_min, pos_max)) |
                                   Q(blade_chassis__rack_position__range=(pos_min, pos_max)))
        else:
            return queryset


class AssetFilter(filters.FilterSet):

    class Meta:
        model = Asset
        fields = ['itmodel', 'asset_number', 'site__offline', 'itmodel__type']


class ChangePlanFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        version = get_version(request)
        return versioned_queryset(
            queryset,
            ChangePlan.objects.get(id=version),
            view.serializer_class.Meta.model.IDENTITY_FIELDS)
