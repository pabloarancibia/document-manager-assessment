from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from ..permissions import OwnFilePermission

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser 

from urllib.parse import unquote


from file_versions.models import FileVersion
from .serializers import FileVersionSerializer

import magic


class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, OwnFilePermission]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"
    parser_classes = (MultiPartParser,)

    def list(self, request):
        ''' get list of files of user
        '''
        filesVersion = FileVersion.objects.filter(file_user=request.user)
        serializer = self.serializer_class(filesVersion, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        ''' Upload new file, 
        if exist similar url and file_name, version_number change
        '''
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            # file name logic, equal to name of file.
            file = request.FILES['url_file']
            if not file:
                raise serializers.ValidationError("Please select a valid file")


            # file version logic
            version_update = 1
            url_setted = request.data.get('url_setted')
            similar_url = FileVersion.objects.filter(url_setted=url_setted)
            if similar_url:
                version_update = len(similar_url) + 1 
                        

            serializer.save(
                version_number=version_update,
                file_name=file)
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PathForFiles(View):

    def get(self, request, *args, **kwargs):
        '''hanging paths for files
    '''
        # get path parameter
        path = kwargs.get('path')  

        # get filename
        filename = unquote(path.split('/')[-1])
        
        # logic to version_number
        if 'revision' in request.GET:
            revision = request.GET['revision']
        else:
            revision = 1
        
        # search fileversion
        # clean path for url_setted
        urlsetted = path
        urlsetted = urlsetted.rsplit('/', 1)[0]  # delete last "/" to final

        # print(path)
        # print(urlsetted)
        # print(revision)
        # print(filename)

        # search file in model
        fileversion = FileVersion.objects.filter(url_setted=urlsetted, version_number=revision, file_name=filename).first()

        # get file url
        if fileversion:
            urlfile = fileversion.url_file
        else:
            return HttpResponse("El archivo no se encontró.", status=404)
        
        # complete path of file
        # full_path = settings.MEDIA_ROOT + '/' + urlfile.path
        full_path = urlfile.path
        
        # open file
        with open(full_path, 'rb') as file:
            file_content = file.read()

        # get type of file with python magic
        mime_type = magic.from_buffer(file_content, mime=True)

        # response file
        response = HttpResponse(file_content, content_type=mime_type)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.name.split('/')[-1])
        return response

