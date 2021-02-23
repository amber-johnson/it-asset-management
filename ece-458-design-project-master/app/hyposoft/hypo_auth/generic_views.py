from rest_framework import generics
from .serializers import PermissionSerializer
from .models import Permission


class PermissionRetrieveView(generics.RetrieveAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
