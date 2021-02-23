from django.urls import path

from .views import ITModelImport, AssetImport, NetworkImport

urlpatterns = [
    path('ITModel', ITModelImport.as_view()),
    path('Asset', AssetImport.as_view()),
    path('Network', NetworkImport.as_view())
]