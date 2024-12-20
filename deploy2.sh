#!/bin/bash

source /home/admin/dehy/dehy/venv/bin/activate && pip install -r requirements.txt && python manage.py collectstatic --noinput --clear && python manage.py makemigrations --noinput && python manage.py migrate && python manage.py thumbnail cleanup && python manage.py thumbnail clear && sudo systemctl daemon-reload && sudo systemctl restart nginx && sudo systemctl restart gunicorn && git status
