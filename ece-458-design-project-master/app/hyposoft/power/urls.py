from django.urls import path

from .list_views import PowerPortList
from .views import get_asset, post_asset, cycle_asset

urlpatterns = [
    path('PowerPortList', PowerPortList.as_view()),

    path('PDUNetwork/get/<int:asset_id>', get_asset),
    path('PDUNetwork/post', post_asset),
    path('PDUNetwork/cycle', cycle_asset)
]
