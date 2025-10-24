# My Cloud Backend

Облачное хранилище файлов - бэкенд на Django REST Framework.

1. Установка и запуск

### Предварительные требования
- Python 3.10+
- PostgreSQL 12+
- Node.js 18+ (для фронтенда)

Клонирование репозитория
bash
git clone <repository-url>
cd my-cloud-backend

2. Настройка виртуального окружения
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Установка зависимостей
bash
pip install -r requirements.txt

4. Настройка базы данных PostgreSQL
sql
CREATE DATABASE mycloud_db;
CREATE USER mycloud_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mycloud_db TO mycloud_user;

5. Настройка переменных окружения
Создайте файл .env в корне проекта:
env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=mycloud_db
DB_USER=mycloud_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

6. Применение миграций
bash
python manage.py makemigrations
python manage.py migrate

7. Создание суперпользователя
bash
python manage.py createsuperuser

8. Запуск сервера
bash
python manage.py runserver