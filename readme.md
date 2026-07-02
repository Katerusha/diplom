Для запуска окружения
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Создание окружения 
python -m venv venv

Запуск окружения
venv\Scripts\Activate.ps1  

зафризить все установленные библиотеки
pip freeze > requirements.txt

Установить все необходимые библиотеки
pip install -r requirements.txt

Для запуска сервера в одной локальной сети
python manage.py runserver 0.0.0.0:8000

#посмотреть ip текущего пк ipconfig

Запуск на всю текущую сеть
1) python manage.py migrate
2) python manage.py runserver 0.0.0.0:8000

http://127.0.0.1:8000/