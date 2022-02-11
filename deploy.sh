#!/bin/bash

activate() {
	./venv/bin/activate
	pip install -r requirements.txt
	python manage.py collectstatic --noinput
	python manage.py makemigrations
	python manage.py migrate

}
activate

# source venv/bin/activate
sudo systemctl daemon-reload
sudo systemctl restart nginx && sudo systemctl restart gunicorn
deactivate