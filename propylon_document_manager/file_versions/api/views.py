from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.conf import settings

from rest_framework import status, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..permissions import OwnFilePermission

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser 

from urllib.parse import unquote


from file_versions.models import FileVersion
from .serializers import FileVersionSerializer

import magic

from drf_spectacular.utils import OpenApiResponse,OpenApiParameter, extend_schema, inline_serializer



class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, OwnFilePermission]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"
    parser_classes = (MultiPartParser,)

    @extend_schema(
        description='Get list of files.\nOnly shows files owned by the user.\nToken Authentication required on header: "Authorization: Token <token>".',
        responses={
            200: FileVersionSerializer(many=True),
            401: OpenApiResponse(
                description='Authentication credentials were not provided.',
                examples={
                    'application/json': {
                        'detail': 'Authentication credentials were not provided.'
                        }
                    }
                )
            }
        )
    def list(self, request):
        '''Get list of files.\n
    Only shows files owned by the user.\n
    Token Authentication required on header: "Authorization: Token \<token\>".
    '''
        filesVersion = FileVersion.objects.filter(file_user=request.user)
        serializer = self.serializer_class(filesVersion, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=inline_serializer(
            name='FileVersionCreate',
            fields={
                'url_setted': serializers.CharField(),
                'url_file': serializers.FileField()
            }
        ),
        responses={
        200: FileVersionSerializer(),
        401: OpenApiResponse(
            description='Authentication credentials were not provided.',
            examples={
                'application/json': {
                    'detail': 'Authentication credentials were not provided.'
                }
            }
        )
    }
    )
    def create(self, request):
        '''Upload a new file. If the file name and URL already exist 
        in the database, a version number will be assigned to 
        the document.\n
        Parameters:\n
        'url_setted': str, Url to upload file\n
        'url_file': file object 
        '''
        
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            # user logged
            user = request.user
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
                file_name=file,
                file_user=user)
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PathForFiles(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, OwnFilePermission]

    @extend_schema(
        description='Paths for download file.\nExample: docs/test/test.pdf\nExample with version: docs/test/test.pdf?revision=2',
        responses={
            200: OpenApiResponse(
                description='File download',
                examples={
                    'application/octet-stream': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }
                }
            ),
            401: OpenApiResponse(
            description='Authentication credentials were not provided.',
            examples={
                'application/json': {
                    'detail': 'Authentication credentials were not provided.'
                }
            }
            ),
            404: OpenApiResponse(description="File not find."),
        }
    )
    def get(self, request, *args, **kwargs):
        '''paths for download file. \n
        example: docs/test/test.pdf \n
        example with version: docs/test/test.pdf?revision=2
    '''
        # get path parameter
        path = kwargs.get('path')  

        # get filename
        filename = unquote(path.split('/')[-1])
        
        
        # search FileVersion object
        # clean path for url_setted
        urlsetted = path
        urlsetted = urlsetted.rsplit('/', 1)[0]  # delete last "/" to final

        # Search file in model
        # logic to version_number
        if 'revision' in request.GET:
            revision = request.GET['revision']
            fileversion = FileVersion.objects.filter(url_setted=urlsetted, version_number=revision, file_name=filename).first()
        else:
            fileversion = FileVersion.objects.filter(url_setted=urlsetted, file_name=filename).last()


        # get file url
        if fileversion:
            urlfile = fileversion.url_file
        else:
            return HttpResponse("File no found.", status=404)
        
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

