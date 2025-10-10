from django.shortcuts import render
import os
from django.http import FileResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserFile
from .serializers import UserFileSerializer, UserFileUploadSerializer, UserFileUpdateSerializer
from .permissions import IsOwnerOrAdmin


class UserFileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                return UserFile.objects.filter(user_id=user_id)
            return UserFile.objects.all()
        else:
            return UserFile.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserFileUploadSerializer
        elif self.action in ['update', 'partial_update']:
            return UserFileUpdateSerializer
        return UserFileSerializer

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        if file_obj:
            serializer.save(
                user=self.request.user,
                original_name=file_obj.name,
                size=file_obj.size
            )
        else:
            raise ValueError("Файл не предоставлен")

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        user_file = self.get_object()
        user_file.last_download = timezone.now()
        user_file.save()

        response = FileResponse(user_file.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{user_file.original_name}"'
        return response

    @action(detail=True, methods=['get'], permission_classes=[])
    def public_download(self, request, unique_identifier=None):
        try:
            user_file = UserFile.objects.get(unique_identifier=unique_identifier)
            user_file.last_download = timezone.now()
            user_file.save()

            response = FileResponse(user_file.file.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{user_file.original_name}"'
            return response
        except UserFile.DoesNotExist:
            return Response({'error': 'Файл не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def generate_link(self, request, pk=None):
        user_file = self.get_object()
        return Response({
            'public_url': f'/api/storage/files/public/{user_file.unique_identifier}/'
        })

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        user_file = self.get_object()
        user_file.last_download = timezone.now()
        user_file.save()

        response = FileResponse(user_file.file.open('rb'))
        # Правильное кодирование имени файла для русского языка
        filename_header = f"attachment; filename*=utf-8''{user_file.original_name}"
        response['Content-Disposition'] = filename_header
        return response
