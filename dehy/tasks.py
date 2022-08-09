from celery import shared_task, Celery
from celery.schedules import crontab
from dehy.appz.checkout.facade import facade

app = Celery()

from .utils import quickbooks, fedex
from oscar.core.loading import get_class, get_model
QuickbooksAuthToken = get_model('generic', 'QuickbooksAuthToken')
FedexAuthToken = get_model('generic', 'FedexAuthToken')

@shared_task
def update_stripe_product_price(sku, price):
	# try:
	# 	product = facade.stripe.Product.retrieve(sku)
	# 	price = facade.stripe.Price.modify(product.default_price, unit_amount=price)
	# except Exception as e:
	# 	print('Error updating stripe product price: ', e)
	product = facade.stripe.Product.retrieve(sku)
	price = facade.stripe.Price.modify(product.default_price, unit_amount=price)

@shared_task
def update_quickbooks_auth_token():
	quickbooks.set_auth_client()
	quickbooks.update_auth_token()

@shared_task
def update_fedex_auth_token():
	fedex.update_auth_token()


# app.conf.beat_schedule = {
#     'fedex-auth-token-every-5-minutes': {
#         'task': 'tasks.update_fedex_auth_token',
#         'schedule': crontab(minute='*/5'),
#     },
# 	'quickbooks-auth-token-every-5-minutes': {
#         'task': 'tasks.update_quickbooks_auth_token',
#         'schedule': crontab(minute='*/5'),
#     },
# }
# app.conf.timezone = 'UTC'
