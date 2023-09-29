#!/bin/bash
python /app/src/manage.py makemigrations app
python /app/src/manage.py migrate
python /app/src/manage.py runserver 0.0.0.0:8000