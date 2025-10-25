from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/login/', views.UserViewSet.as_view({'post': 'login'}), name='login'),
    path('api/auth/logout/', views.UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('api/auth/register/', views.UserViewSet.as_view({'post': 'register'}), name='register'),
    path('api/stats/', views.UserViewSet.as_view({'get': 'stats'}), name='stats'),
]