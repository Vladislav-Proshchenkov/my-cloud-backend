from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.UserFileViewSet, basename='userfile')

urlpatterns = [
    path('api/storage/', include(router.urls)),

    path('api/storage/files/<int:pk>/download/',
         views.UserFileViewSet.as_view({'get': 'download'}),
         name='file-download'),
    path('api/storage/files/<int:pk>/preview/',
         views.UserFileViewSet.as_view({'get': 'preview'}),
         name='file-preview'),
    path('api/storage/files/<int:pk>/share/',
         views.UserFileViewSet.as_view({'post': 'share'}),
         name='file-share'),
    path('api/storage/files/public/<uuid:unique_identifier>/info/',
         views.UserFileViewSet.as_view({'get': 'public_info'}),
         name='public-file-info'),
    path('api/storage/files/public/<uuid:unique_identifier>/download/',
         views.UserFileViewSet.as_view({'get': 'public_download'}),
         name='public-file-download'),
]