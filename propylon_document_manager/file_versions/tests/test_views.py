import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

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
    file_version_1 = FileVersion.objects.create(**file_version_data)
    file_version_2 = FileVersion.objects.create(**file_version_data)

    response = authenticated_api_client.get('/api/file_versions/')
    assert response.status_code == 200

    serializer = FileVersionSerializer([file_version_1, file_version_2], many=True)
    assert response.data == serializer.data

@pytest.mark.django_db
@pytest.mark.parametrize('file_version_data', [{'file_name': 'test3.txt', 'url_setted': 'url3'}], indirect=True)
def test_file_version_increment_version_number(authenticated_api_client, file_version_data):
    # initial file version for the authenticated user
    user = User.objects.get(email='testuser@admin.com')
    initial_file_version = FileVersion.objects.create(
        url_setted=file_version_data['url_setted'],
        file=file_version_data['url_file'],
        file_user=user,
    )

    # second file version with the same url_setted and file_name
    second_file_version = FileVersion.objects.create(
        url_setted=file_version_data['url_setted'],
        file=file_version_data['url_file'],
        file_user=user,
    )

    # Verify that the version_number of the second file version is incremented
    assert second_file_version.version_number == initial_file_version.version_number + 1

@pytest.mark.django_db
@pytest.mark.parametrize('file_version_data', [{'file_name': 'test3.txt', 'url_setted': 'url3'}], indirect=True)
def test_file_version_create(authenticated_api_client, file_version_data):
    # create file
    response = authenticated_api_client.post('/api/file-versions/', data=file_version_data, format='multipart')
    assert response.status_code == 201

    # recover id of file
    file_version_id = response.data['id']
    # search file
    file_version = FileVersion.objects.get(id=file_version_id)
    # send to serializer
    serializer = FileVersionSerializer(file_version)
    # verify
    assert response.data == serializer.data

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
