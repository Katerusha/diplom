Для запуска окружения
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1  

Для запуска сервера в одной локальной сети
python manage.py runserver 0.0.0.0:8000

#посмотреть ip текущего пк ipconfig

зафризить все установленные библиотеки
pip freeze > requirements.txt