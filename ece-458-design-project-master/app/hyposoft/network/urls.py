from django.urls import path

from .list_views import NetworkPortList, NetworkGraph

urlpatterns = [
    path('NetworkPortList', NetworkPortList.as_view()),
    path('NetworkGraph/<int:asset_id>', NetworkGraph.as_view())
]
