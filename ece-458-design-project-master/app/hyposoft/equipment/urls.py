from django.urls import path

from .views import *
from .list_views import *
from .report_views import Report

urlpatterns = [
    path('ITModelCreate', ITModelCreate.as_view()),
    path('AssetCreate', AssetCreate.as_view()),
    path('RackRangeCreate', RackRangeCreate.as_view()),
    path('SiteCreate', SiteCreate.as_view()),

    path('ITModelUpdate/<int:pk>', ITModelUpdate.as_view()),
    path('AssetUpdate/<int:pk>', AssetUpdate.as_view()),
    path('SiteUpdate/<int:pk>', SiteUpdate.as_view()),

    path('ITModelDestroy/<int:pk>', ITModelDestroy.as_view()),
    path('AssetDestroy/<int:pk>', AssetDestroy.as_view()),
    path('RackRangeDestroy', RackRangeDestroy.as_view()),
    path('SiteDestroy/<int:pk>', SiteDestroy.as_view()),

    path('ITModelRetrieve/<int:pk>', ITModelRetrieve.as_view()),
    path('AssetRetrieve/<int:pk>', AssetRetrieve.as_view()),
    path('AssetDetailRetrieve/<int:pk>', AssetDetailRetrieve.as_view()),

    path('ITModelList', ITModelList.as_view()),
    path('ITModelPickList', ITModelPickList.as_view()),
    path('VendorList', VendorList.as_view()),
    path('AssetList', AssetList.as_view()),
    path('AssetPickList', AssetPickList.as_view()),
    path('DecommissionedAssetList', DecommissionedAssetList.as_view()),

    path('RackList', RackList.as_view()),
    path('SiteList', SiteList.as_view()),

    path('rack_view', RackView.as_view()),
    path('report', Report.as_view()),

    path('DecommissionAsset/<int:asset_id>', DecommissionAsset.as_view()),

    path('AssetIDForAssetNumber/<int:asset_number>', AssetIDForAssetNumber.as_view()),
]
