from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class UserModelTestCase(TestCase):
    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123!Password'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_admin)
        self.assertTrue(user.check_password('Test123!Password'))

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin123!Password'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_username_validation(self):
        """Тест валидации имени пользователя"""
        valid_usernames = ['user123', 'TestUser', 'hello123']
        for username in valid_usernames:
            with self.subTest(username=username):
                user = User(
                    username=username,
                    email='test@example.com',
                    password='ValidPassword123!'
                )
                user.full_clean()


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Valid123!Password',
            'password_confirm': 'Valid123!Password',
            'first_name': 'New',
            'last_name': 'User'
        }

    def test_successful_registration(self):
        """Тест успешной регистрации"""
        response = self.client.post('/api/users/register/', self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertFalse(user.is_admin)

    def test_registration_duplicate_username(self):
        """Тест регистрации с существующим username"""
        User.objects.create_user(username='existing', email='exist@example.com', password='test123')

        data = self.valid_data.copy()
        data['username'] = 'existing'

        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_password_validation(self):
        """Тест валидации пароля"""
        invalid_passwords = [
            'short',  # слишком короткий
            'nouppercase123!',  # нет заглавной
            'NOLOWERCASE123!',  # нет строчной
            'NoNumbers!',  # нет цифр
            'NoSpecial123',  # нет спецсимвола
        ]

        for password in invalid_passwords:
            with self.subTest(password=password):
                data = self.valid_data.copy()
                data['password'] = password
                data['password_confirm'] = password

                response = self.client.post('/api/users/register/', data)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('password', response.data)


class UserAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test123!Password'
        )
        self.client = APIClient()

    def test_successful_login(self):
        """Тест успешного входа"""
        data = {
            'username': 'testuser',
            'password': 'Test123!Password'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Тест выхода из системы"""
        # Сначала логинимся
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/users/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAdminTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='Admin123!Password',
            is_admin=True
        )
        self.user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='User123!Password'
        )
        self.client.force_authenticate(user=self.admin)

    def test_admin_can_get_users_list(self):
        """Тест что админ может получить список пользователей"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin + regularuser

    def test_regular_user_cannot_get_users_list(self):
        """Тест что обычный пользователь не может получить список пользователей"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        """Тест удаления пользователя"""
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='delete@example.com',
            password='Test123!'
        )

        response = self.client.delete(f'/api/users/{user_to_delete.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='todelete')