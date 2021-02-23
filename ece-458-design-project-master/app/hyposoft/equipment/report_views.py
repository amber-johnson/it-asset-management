from django.contrib.auth.models import User
from rest_framework import views
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from equipment.models import ITModel, Site, Rack
from hyposoft.utils import get_site


class Report(views.APIView):
    def get_vendor(self, vendor, my_site):
        itmodels = ITModel.objects.filter(vendor=vendor, type__in=(ITModel.Type.REGULAR, ITModel.Type.CHASSIS))
        total_space = 0
        used_space = 0
        if my_site:
            racks = Rack.objects.filter(site=my_site, version_id=0)
            for rack in racks:
                total_space += 42
                for asset in rack.asset_set.filter(blade_chassis=None):
                    if asset.itmodel in itmodels:
                        used_space += asset.itmodel.height
        else:
            for site in Site.objects.all():
                racks = Rack.objects.filter(site=site, version_id=0)
                for rack in racks:
                    total_space += 42
                    for asset in rack.asset_set.filter(blade_chassis=None):
                        if asset.itmodel in itmodels:
                            used_space += asset.itmodel.height
        try:
            used = used_space / total_space
            free = (total_space - used_space) / total_space
        except:
            used = 0
            free = 0
        msg = {"category": vendor, "used": used, "free": free}
        return msg

    def get_model(self, model, my_site):
        total_space = 0
        used_space = 0
        if my_site:
            racks = Rack.objects.filter(site=my_site, version_id=0)
            for rack in racks:
                total_space += 42
                for asset in rack.asset_set.filter(blade_chassis=None):
                    if asset.itmodel == model:
                        used_space += asset.itmodel.height
        else:
            for site in Site.objects.all():
                racks = Rack.objects.filter(site=site, version_id=0)
                for rack in racks:
                    total_space += 42
                    for asset in rack.asset_set.filter(blade_chassis=None):
                        if asset.itmodel == model:
                            used_space += asset.itmodel.height
        try:
            used = used_space / total_space
            free = (total_space - used_space) / total_space
        except:
            used = 0
            free = 0
        msg = {"category": str(model), "used": used, "free": free}
        return msg

    def get_owner(self, my_owner, my_site):
        total_space = 0
        used_space = 0
        if my_site:
            racks = Rack.objects.filter(site=my_site, version_id=0)
            for rack in racks:
                total_space += 42
                rack_assets = rack.asset_set.filter(blade_chassis=None, owner=my_owner)
                for asset in rack_assets:
                    used_space += asset.itmodel.height
        else:
            for site in Site.objects.all():
                racks = Rack.objects.filter(site=site, version_id=0)
                for rack in racks:
                    total_space += 42
                    rack_assets = rack.asset_set.filter(blade_chassis=None, owner=my_owner)
                    for asset in rack_assets:
                        used_space += asset.itmodel.height
        try:
            used = used_space / total_space
            free = (total_space - used_space) / total_space
        except:
            used = 0
            free = 0
        msg = {"category": my_owner.username, "used": used,"free": free}
        return msg

    def get(self, request):
        try:
            site = Site.objects.get(id=get_site(request))
        except:
            site = None
        models = [self.get_model(model, site)
                  for model in ITModel.objects.filter(type__in=(ITModel.Type.REGULAR, ITModel.Type.CHASSIS))]
        owners = [self.get_owner(owner, site) for owner in User.objects.all()]
        vendors = [self.get_vendor(vendor, site)
                   for vendor in ITModel.objects.values_list('vendor', flat=True).distinct('vendor')]

        used = 0
        for model in ITModel.objects.filter(type__in=(ITModel.Type.REGULAR, ITModel.Type.CHASSIS)):
            used += model.asset_set.filter(blade_chassis=None, version_id=0).count()

        if site:
            total = Rack.objects.filter(site=site, version_id=0).count()
        else:
            total = Rack.objects.filter(version_id=0).count()
        total *= 42

        try:
            used = used / total
            free = (total - used) / total
        except:
            used = 0
            free = 0
        return Response({
            'total': [{"category": "total", "used": used, "free": free}],
            'by_model': models,
            'by_owner': owners,
            'by_vendor': vendors
        }, status=HTTP_200_OK)
