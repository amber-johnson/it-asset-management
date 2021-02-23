from django.contrib import admin
from .models import ChangePlan, AssetDiff, NetworkPortDiff, PoweredDiff


admin.site.register(ChangePlan)
admin.site.register(AssetDiff)
admin.site.register(NetworkPortDiff)
admin.site.register(PoweredDiff)
