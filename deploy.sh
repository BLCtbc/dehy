#!/bin/sh
cd ~/home/admin/dehy/dehy
source venv/bin/activate
git checkout staging
git pull
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
echo 'hello world'
python manage.py collectstatic --noinput
sudo systemctl restart nginx
sudo systemctl restart gunicorn
