#!/bin/sh
cd ~/home/admin/dehy/dehy
git checkout staging
git pull
python manage.py makemigrations
python manage.py migrate
source venv/bin/activate
pip install -r requirements.txt
echo 'hello world'
python manage.py collectstatic --noinput
sudo systemctl restart nginx && sudo systemctl restart gunicorn
