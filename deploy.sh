#!/bin/sh
cd ~/home/admin/dehy/dehy
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
git checkout staging
git pull
python manage.py makemigrations
python manage.py migrate
echo 'hello world'
python manage.py collectstatic --noinput
sudo systemctl restart nginx
sudo systemctl restart gunicorn
