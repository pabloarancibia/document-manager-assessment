import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status

from propylon_document_manager.file_versions.models import FileVersion
from propylon_document_manager.file_versions.api.serializers import FileVersionSerializer

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client):
    user = User.objects.create_user(email='testuser@admin.com', password='test-password')
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return api_client

@pytest.fixture
def file_version_data(request):
    file_name = request.param.get('file_name', 'test.txt')
    url_setted = request.param.get('url_setted', 'test-url')

    file_content = request.param.get('file_content', b"File content")
    file = SimpleUploadedFile(file_name, file_content)

    return {
        'url_file': file,
        'url_setted': url_setted,
    }

@pytest.mark.django_db
@pytest.mark.parametrize('file_version_data', [{'file_name': 'test1.txt', 'url_setted': 'url1'}, {'file_name': 'test2.txt', 'url_setted': 'url2'}], indirect=True)
def test_file_version_list(authenticated_api_client, file_version_data):
    # Create some file versions for the authenticated user
    user = User.objects.get(email='testuser@admin.com')
    file_version = FileVersion.objects.create(**file_version_data, file_user=user)
    #file_version_1 = FileVersion.objects.create(**file_version_data)
    #file_version_2 = FileVersion.objects.create(**file_version_data)

    response = authenticated_api_client.get('/api/file_versions/')
    assert response.status_code == 200

    serializer = FileVersionSerializer([file_version], many=True)
    assert response.data == serializer.data

@pytest.mark.django_db
@pytest.mark.parametrize('file_version_data', [{'file_name': 'test3.txt', 'url_setted': 'url3'}], indirect=True)
def test_file_version_create(authenticated_api_client, file_version_data):
    # create file
    response = authenticated_api_client.post('/api/file_versions/', data=file_version_data, format='multipart')

    # recover id of file
    file_version_id = response.data['id']
    # search file
    file_version = FileVersion.objects.get(id=file_version_id)
    # send to serializer
    serializer = FileVersionSerializer(file_version)
    # verify
    assert response.data == serializer.data and response.status_code == 200

# endpoints for download files tests:
@pytest.mark.django_db
@pytest.mark.parametrize('file_version_data', [{'file_name': 'test4.txt', 'url_setted': 'url4'}], indirect=True)
def test_path_for_files(authenticated_api_client, file_version_data):
    # Create a file version for the authenticated user
    user = User.objects.get(email='testuser@admin.com')
    file_version = FileVersion.objects.create(
        url_setted=file_version_data['url_setted'],
        url_file=file_version_data['url_file']
    )
    file_path = file_version.url_file.path

    response = authenticated_api_client.get(f"/api/{file_version_data['url_setted']}/")
    assert response.status_code == 200

    expected_content = open(file_path, 'rb').read()
    assert response.content == expected_content


@pytest.mark.django_db
def test_path_for_files_file_not_found(authenticated_api_client):
    response = authenticated_api_client.get('/api/nonexistent-url/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_file_version(api_client):

    file_version_data = {
        'file_name': 'test.txt',
        'url_setted': 'test-url',
    }

    response = api_client.post('/api/file-versions/', data=file_version_data, format='multipart')


    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
