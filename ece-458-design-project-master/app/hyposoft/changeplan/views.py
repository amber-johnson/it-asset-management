from django.db import transaction
from django.utils.timezone import now
from rest_framework import generics, serializers
from rest_framework import views
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from equipment.handlers import decommission_asset
from equipment.models import Rack, Asset, ITModel
from equipment.views import DecommissionAsset
from hyposoft.utils import versioned_object
from network.models import NetworkPort
from power.models import PDU, Powered
from .handlers import execute_assets, \
    execute_networkports, execute_powereds, get_asset, get_power, get_network, create_asset_diffs, create_powered_diffs, \
    create_networkport_diffs
from .models import ChangePlan
from .serializers import ChangePlanSerializer, ChangePlanDetailSerializer


class ExecuteChangePlan(views.APIView):
    @transaction.atomic
    def post(self, request, pk):
        try:
            # Get ChangePlan
            changeplan = ChangePlan.objects.get(id=pk)
            live = ChangePlan.objects.get(id=0)
            children = changeplan.changeplan_set.all()
            # Record diff for future reference
            create_asset_diffs(changeplan, live)
            create_powered_diffs(changeplan, live)
            create_networkport_diffs(changeplan, live)
            # Update Objects
            execute_assets(changeplan)
            execute_networkports(changeplan)
            execute_powereds(changeplan)
            changeplan.executed = True
            changeplan.executed_at = now()
            changeplan.save()
            for child in children:
                asset = Asset.objects.get(version=child, commissioned__isnull=True)
                live_asset = versioned_object(asset, ChangePlan.objects.get(id=0), Asset.IDENTITY_FIELDS)
                if live_asset:
                    decommission_asset(live_asset.id, DecommissionAsset(), request.user, live)
                    print('DECOMMISSIONED')

                for model in (Powered, NetworkPort, Asset, PDU, Rack):
                    if model == Asset:
                        model.objects.filter(version=child, itmodel__type=ITModel.Type.BLADE).delete()
                    model.objects.filter(version=child).delete()

                child.delete()
            return Response(ChangePlanDetailSerializer(changeplan).data, status=HTTP_200_OK)
        except Exception as e:
            raise serializers.ValidationError("This ChangePlan is not valid.")


class UserChangePlansMixin():
    def get_queryset(self):
        return ChangePlan.objects.filter(owner=self.request.user, auto_created=False, id__gt=0)


class ChangePlanList(UserChangePlansMixin, generics.ListAPIView):
    serializer_class = ChangePlanSerializer


class ChangePlanDetails(UserChangePlansMixin, generics.RetrieveAPIView):
    serializer_class = ChangePlanDetailSerializer


class ChangePlanCreate(UserChangePlansMixin, generics.CreateAPIView):
    serializer_class = ChangePlanSerializer


class ChangePlanDestroy(UserChangePlansMixin, generics.DestroyAPIView):
    serializer_class = ChangePlanSerializer

    def destroy(self, request, *args, **kwargs):
        version = self.get_object()

        # Order matters!
        for model in (Powered, NetworkPort, Asset, PDU, Rack):
            if model == Asset:
                model.objects.filter(version=version, itmodel__type=ITModel.Type.BLADE).delete()
            model.objects.filter(version=version).delete()

        return super(ChangePlanDestroy, self).destroy(request, *args, **kwargs)


class ChangePlanUpdate(UserChangePlansMixin, generics.UpdateAPIView):
    serializer_class = ChangePlanSerializer


class ChangePlanActions(views.APIView):
    def get(self, request, pk):
        changeplan = ChangePlan.objects.get(id=pk)
        live = ChangePlan.objects.get(id=0)
        messages = []

        asset_diff = get_asset(changeplan, live)
        power_diff = get_power(changeplan, live)
        network_diff = get_network(changeplan, live)

        for diff in asset_diff:
            if diff['live']:
                messages += ["#{}: {}".format(diff['live'].asset_number, message) for message in diff['messages']]

        for diff in power_diff:
            if diff['live']:
                messages += ["#{}: {}".format(diff['live'].asset.asset_number, message) for message in diff['messages']]
            else:
                messages += diff['messages']

        for diff in network_diff:
            if diff['live']:
                messages += ["#{} – {}: {}".format(
                    diff['live'].asset.asset_number, diff['live'].label.name, message) for message in diff['messages']]
            else:
                messages += diff['messages']

        return Response(messages, status=HTTP_200_OK)
