from django.db import models, router
from django.db.models import F, signals
from dehy.tasks import update_stripe_product_price

from oscar.apps.partner.abstract_models import AbstractStockRecord

class StockRecord(AbstractStockRecord):

	def save(self, *args, **kwargs):

		super().save(*args, **kwargs)
		print('dir(self): ', dir(self))
		update_stripe_product_price.delay(self.partner_sku, int(stock_record.price*100))


	class Meta:
		# order_with_respect_to =
		ordering = ['price']

from oscar.apps.partner.models import *  # noqa isort:skip
