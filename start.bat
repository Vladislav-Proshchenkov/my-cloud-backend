@echo off
echo Starting My Cloud Application...
echo.

echo Starting Django Backend...
cd my-cloud-backend
call venv\Scripts\activate
start cmd /k "python manage.py runserver"
cd ..

echo Starting React Frontend...
cd my-cloud-frontend
start cmd /k "npm start"
cd ..

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause