#!/bin/bash

sleep 10;

# Cambiar al directorio del proyecto Django
#cd /code;

# Realizar las migraciones de la base de datos
python manage.py migrate;
python manage.py makemigrations;
python manage.py migrate;

# Iniciar Gunicorn para ejecutar la aplicación Django
gunicorn --bind :8000 proyecto.wsgi:application --reload
#python manage.py runserver 0.0.0.0:8000
