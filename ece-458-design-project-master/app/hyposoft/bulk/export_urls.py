from django.urls import path

from .views import ITModelExport, AssetExport, NetworkExport

urlpatterns = [
    path('ITModel.csv', ITModelExport.as_view()),
    path('Asset.csv', AssetExport.as_view()),
    path('Network.csv', NetworkExport.as_view())
]