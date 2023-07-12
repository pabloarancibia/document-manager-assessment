from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from ..permissions import OwnFilePermission

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response

from file_versions.models import FileVersion
from .serializers import FileVersionSerializer

class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, OwnFilePermission]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    def list(self, request):
        filesVersion = FileVersion.objects.filter(file_user=request.user)
        serializer = self.serializer_class(filesVersion, many=True)
        return Response(serializer.data)
