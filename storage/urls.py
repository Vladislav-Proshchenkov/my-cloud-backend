from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.UserFileViewSet, basename='file')

urlpatterns = [
    path('api/storage/', include(router.urls)),
    path('storage/files/public/<uuid:unique_identifier>/info/',
         views.UserFileViewSet.as_view({'get': 'public_info'}),
         name='public-file-info'),
    path('storage/files/public/<uuid:unique_identifier>/download/',
         views.UserFileViewSet.as_view({'get': 'public_download'}),
         name='public-file-download'),
]