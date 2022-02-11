#!/bin/sh
source venv/bin/activate
git checkout staging
git pull
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart nginx
sudo systemctl restart gunicorn
