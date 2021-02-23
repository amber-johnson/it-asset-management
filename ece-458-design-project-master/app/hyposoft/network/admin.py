from django.contrib import admin
from .models import NetworkPortLabel, NetworkPort
from .resources import NetworkPortResource
from import_export.admin import ImportExportActionModelAdmin
from import_export.formats import base_formats


class NetworkPortAdmin(ImportExportActionModelAdmin):
    resource_class = NetworkPortResource
    formats = (base_formats.CSV,)
    from_encoding = 'utf-8-sig'
    list_filter = ['networkport__asset', 'networkport__label']


admin.site.register(NetworkPortLabel, NetworkPortAdmin)
admin.site.register(NetworkPort)
