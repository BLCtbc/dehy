#!/bin/bash

source /home/admin/dehy/dehy/venv/bin/activate && pip install -r requirements.txt && python manage.py collectstatic --noinput --clear && python manage.py makemigrations && python manage.py migrate && python manage.py thumbnail cleanup && python manage.py thumbnail clear
