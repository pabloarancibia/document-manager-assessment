from django.shortcuts import render

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from file_versions.models import FileVersion
from .serializers import FileVersionSerializer

# class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
class FileVersionViewSet(ModelViewSet):
    #authentication_classes = []
    #permission_classes = []
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    #lookup_field = "id"
