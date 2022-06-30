from oscar.core.loading import get_class, get_model
from celery import shared_task, Celery
from celery.schedules import crontab

app = Celery()

from .utils import quickbooks, fedex

# QuickbooksAuthToken = get_model('generic', 'QuickbooksAuthToken')
# FedexAuthToken = get_model('generic', 'FedexAuthToken')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
	#
    # # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(minute=*/5),
        update_quickbooks_auth_token.s(),
    )

	sender.add_periodic_task(
        crontab(minute=*/5),
        update_fedex_auth_token.s(),
    )



@shared_task
def update_quickbooks_auth_token():
	quickbooks.set_auth_client()
	quickbooks.update_auth_token()

@shared_task
def update_fedex_auth_token():
	fedex.update_auth_token()
