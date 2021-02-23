from rest_framework import generics, views
from rest_framework.response import Response

from equipment.list_views import FilterBySiteMixin
from .handlers import net_graph
from .models import NetworkPort
from .serializers import NetworkPortSerializer


class NetworkPortList(FilterBySiteMixin, generics.ListAPIView):
    def get_queryset(self):
        return NetworkPort.objects.filter(asset__decommissioned_timestamp=None)

    serializer_class = NetworkPortSerializer


class NetworkGraph(views.APIView):
    def get(self, request, asset_id):
        return Response(net_graph(asset_id))
