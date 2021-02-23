from django.contrib import admin
from django.urls import path, include
from .users import UserList
from django.conf.urls import url


urlpatterns = [
    path('', include('frontend.urls')),
    path('auth/', include('hypo_auth.urls')),
    path('admin/', admin.site.urls),
    path('api/equipment/', include('equipment.urls')),
    path('api/network/', include('network.urls')),
    path('api/power/', include('power.urls')),
    path('api/changeplan/', include('changeplan.urls')),
    path('api/log/', include('system_log.urls')),
    path('api/import/', include('bulk.import_urls')),
    path('api/export/', include('bulk.export_urls')),
    path('api/users/UserList/', UserList.as_view()),
    path('api/auth/', include('rest_framework.urls')),
]

