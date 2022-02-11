#!/bin/sh
source venv/bin/activate
git pull origin staging
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart nginx
sudo systemctl restart gunicorn
