@echo off
cd /d D:\project1
call venv\Scripts\activate
python manage.py runserver
pause