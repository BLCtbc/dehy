#!/bin/sh

source "./venv/bin/activate" && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py makemigrations && python manage.py migrate
sudo systemctl daemon-reload
sudo systemctl restart nginx && sudo systemctl restart gunicorn