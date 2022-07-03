from django.db import models, router
from django.db.models import F, signals
from dehy.tasks import update_stripe_product_price

from oscar.apps.partner.abstract_models import AbstractStockRecord

class StockRecord(AbstractStockRecord):

	def save(self, *args, **kwargs):

		super().save(*args, **kwargs)
		update_stripe_product_price.delay(self.partner_sku, int(self.price*100))


	class Meta:
		# order_with_respect_to =
		ordering = ['price']

from oscar.apps.partner.models import *  # noqa isort:skip
