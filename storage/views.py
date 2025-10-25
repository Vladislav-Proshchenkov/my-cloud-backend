from django.shortcuts import render
import os
from django.http import FileResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
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
        user_id = self.request.query_params.get('user_id')
        if user_id and user.is_admin:
            return UserFile.objects.filter(user_id=user_id)
        else:
            return UserFile.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    @action(detail=True, methods=['patch'])
    def update_info(self, request, pk=None):
        user_file = self.get_object()
        serializer = UserFileUpdateSerializer(user_file, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='public/(?P<unique_identifier>[^/.]+)/info', url_name='public-info')
    def public_info(self, request, unique_identifier=None):
        try:
            user_file = UserFile.objects.get(unique_identifier=unique_identifier)
            serializer = self.get_serializer(user_file)
            return Response(serializer.data)
        except UserFile.DoesNotExist:
            return Response({'error': 'Файл не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='public/(?P<unique_identifier>[^/.]+)/download',
            url_name='public-download')
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

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        user_file = self.get_object()

        if not user_file.file:
            return Response(
                {"error": "Файл не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        content_type = 'application/octet-stream'
        if user_file.original_name.lower().endswith(('.txt', '.pdf', '.jpg', '.jpeg', '.png', '.gif')):
            if user_file.original_name.lower().endswith('.txt'):
                content_type = 'text/plain'
            elif user_file.original_name.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif user_file.original_name.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif user_file.original_name.lower().endswith('.png'):
                content_type = 'image/png'
            elif user_file.original_name.lower().endswith('.gif'):
                content_type = 'image/gif'

        user_file.last_download = timezone.now()
        user_file.save()

        response = FileResponse(user_file.file.open('rb'), content_type=content_type)

        if content_type == 'application/octet-stream':
            response['Content-Disposition'] = f'attachment; filename="{user_file.original_name}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{user_file.original_name}"'

        return response

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        user_file = self.get_object()
        user_file.is_public = True
        user_file.save()
        return Response({
            'public_url': f'/file/{user_file.unique_identifier}'
        })

    def create_share(self, request, pk=None):
        user_file = self.get_object()
        user_file.is_public = True
        user_file.save()
        return Response({
            'public_url': f'/api/public/files/{user_file.unique_identifier}/'
        })

    def delete_share(self, request, pk=None):
        user_file = self.get_object()
        user_file.is_public = False
        user_file.save()
        return Response({'message': 'Публичная ссылка удалена'})