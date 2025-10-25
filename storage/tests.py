from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserFile

User = get_user_model()


class UserFileModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

    def test_file_creation(self):
        """Тест создания файла"""
        file = UserFile.objects.create(
            user=self.user,
            original_name='test.txt',
            size=100,
            comment='Test file'
        )
        self.assertEqual(file.original_name, 'test.txt')
        self.assertEqual(file.user.username, 'testuser')
        self.assertEqual(file.comment, 'Test file')
        self.assertIsNotNone(file.unique_identifier)

    def test_file_string_representation(self):
        """Тест строкового представления файла"""
        file = UserFile.objects.create(
            user=self.user,
            original_name='test.txt',
            size=100
        )
        self.assertEqual(str(file), 'test.txt (testuser)')

    def test_file_auto_size_calculation(self):
        """Тест автоматического расчета размера файла"""
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"file content for size test",
            content_type="text/plain"
        )

        file_obj = UserFile.objects.create(
            user=self.user,
            original_name='test_file.txt',
            file=test_file
        )

        self.assertEqual(file_obj.size, len(b"file content for size test"))

    def test_file_deletion_removes_physical_file(self):
        """Тест что удаление файла удаляет физический файл"""
        test_file = SimpleUploadedFile(
            "test_file.txt",
            b"file content",
            content_type="text/plain"
        )

        file_obj = UserFile.objects.create(
            user=self.user,
            original_name='test_file.txt',
            file=test_file,
            size=len(b"file_content")
        )

        file_path = file_obj.file.path
        self.assertTrue(os.path.exists(file_path))

        file_obj.delete()
        self.assertFalse(os.path.exists(file_path))


class UserFileAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123!Password'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin123!Password',
            is_admin=True
        )
        self.client.force_authenticate(user=self.user)

        self.test_file = SimpleUploadedFile(
            "test.txt",
            b"test file content",
            content_type="text/plain"
        )

    def test_upload_file(self):
        """Тест загрузки файла"""
        data = {
            'file': self.test_file,
            'comment': 'Test file comment'
        }

        response = self.client.post('/api/storage/files/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        file_obj = UserFile.objects.get(original_name='test.txt')
        self.assertEqual(file_obj.comment, 'Test file comment')
        self.assertEqual(file_obj.user, self.user)

    def test_get_files_list(self):
        """Тест получения списка файлов"""
        UserFile.objects.create(user=self.user, original_name='file1.txt', size=100)
        UserFile.objects.create(user=self.user, original_name='file2.txt', size=200)

        response = self.client.get('/api/storage/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthorized_access(self):
        """Тест неавторизованного доступа к файлам"""
        self.client.logout()
        response = self.client.get('/api/storage/files/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_other_user_files(self):
        """Тест доступа к файлам другого пользователя"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Other123!Password'
        )

        other_file = UserFile.objects.create(
            user=other_user,
            original_name='other_file.txt',
            size=100
        )

        response = self.client.get('/api/storage/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_files = [f for f in response.data if f['user'] == self.user.id]
        self.assertEqual(len(user_files), 0)

    def test_admin_access_all_files(self):
        """Тест что админ может видеть все файлы"""
        self.client.force_authenticate(user=self.admin)

        UserFile.objects.create(user=self.user, original_name='user_file.txt', size=100)
        UserFile.objects.create(user=self.admin, original_name='admin_file.txt', size=200)

        response = self.client.get('/api/storage/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_file(self):
        """Тест удаления файла"""
        file_obj = UserFile.objects.create(
            user=self.user,
            original_name='delete_me.txt',
            size=100
        )

        response = self.client.delete(f'/api/storage/files/{file_obj.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(UserFile.DoesNotExist):
            UserFile.objects.get(id=file_obj.id)