import requests
import json
import pytest

BASE_URL = 'http://localhost:8000/api'


class TestAPIIntegration:
    def setup_method(self):
        self.session = requests.Session()
        self.auth_data = {
            'username': 'testuser',
            'password': 'Test123!Password'
        }

    def test_user_registration_and_file_upload(self):
        """Интеграционный тест: регистрация + загрузка файла"""
        reg_data = {
            'username': 'integration_user',
            'email': 'integration@example.com',
            'password': 'Integration123!',
            'password_confirm': 'Integration123!'
        }

        reg_response = self.session.post(f'{BASE_URL}/users/register/', json=reg_data)
        assert reg_response.status_code == 201

        login_response = self.session.post(
            f'{BASE_URL}/users/login/',
            json={'username': 'integration_user', 'password': 'Integration123!'}
        )
        assert login_response.status_code == 200

        files = {'file': ('test.txt', b'integration test content', 'text/plain')}
        data = {'comment': 'Integration test file'}

        upload_response = self.session.post(
            f'{BASE_URL}/storage/files/',
            files=files,
            data=data
        )
        assert upload_response.status_code == 201

        files_response = self.session.get(f'{BASE_URL}/storage/files/')
        assert files_response.status_code == 200
        assert len(files_response.json()) == 1

    def test_public_link_workflow(self):
        """Интеграционный тест: создание публичной ссылки и скачивание"""
        self.session.post(f'{BASE_URL}/users/login/', json=self.auth_data)

        files = {'file': ('public_test.txt', b'public content', 'text/plain')}
        upload_response = self.session.post(f'{BASE_URL}/storage/files/', files=files)
        file_id = upload_response.json()['id']

        link_response = self.session.post(f'{BASE_URL}/storage/files/{file_id}/generate_link/')
        assert link_response.status_code == 200
        public_url = link_response.json()['public_url']

        new_session = requests.Session()
        download_response = new_session.get(f'http://localhost:8000{public_url}')
        assert download_response.status_code == 200