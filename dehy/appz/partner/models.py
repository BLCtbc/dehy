from oscar.apps.partner.abstract_models import AbstractStockRecord

class StockRecord(AbstractStockRecord):
	class Meta:
		# order_with_respect_to = 
		ordering = ['price']

from oscar.apps.partner.models import *  # noqa isort:skip
