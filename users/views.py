from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from storage.models import UserFile
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer
from .permissions import IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Пользователь успешно зарегистрирован',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Успешный вход в систему',
                'user': UserSerializer(user).data
            })
        return Response({
            'error': 'Неверный логин или пароль'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Успешный выход из системы'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def toggle_admin(self, request, pk=None):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_admin = not user.is_admin
        user.save()
        action = 'назначен' if user.is_admin else 'снят'
        return Response({
            'message': f'Пользователю {user.username} {action} статус администратора'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        users_stats = CustomUser.objects.annotate(
            file_count=Count('userfile'),
            total_size=Sum('userfile__size')
        ).values('id', 'username', 'file_count', 'total_size')

        total_stats = {
            'total_users': CustomUser.objects.count(),
            'total_files': UserFile.objects.count(),
            'total_storage_used': UserFile.objects.aggregate(Sum('size'))['size__sum'] or 0,
            'admin_count': CustomUser.objects.filter(is_admin=True).count(),
        }

        return Response({
            'users_stats': list(users_stats),
            'total_stats': total_stats
        })