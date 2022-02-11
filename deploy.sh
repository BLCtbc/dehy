#!/bin/sh
cd ~/home/admin/dehy/dehy
git pull
source venv/bin/activate
pip install -r requirements.txt
echo 'hello world'
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
sudo systemctl daemon-reload
sudo systemctl restart nginx && sudo systemctl restart gunicorn
