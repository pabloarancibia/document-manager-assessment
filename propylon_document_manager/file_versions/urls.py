from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import FileVersionViewSet

router = DefaultRouter()
router.register('file',FileVersionViewSet,basename='files')

urlpatterns = [
    path('', include(router.urls)),
]