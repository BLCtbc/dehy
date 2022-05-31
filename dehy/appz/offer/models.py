from oscar.apps.offer.models import Benefit as BaseBenefit
from decimal import Decimal as D

class Benefit(BaseBenefit):
	def shipping_discount(self, charge, currency=None):
		return D(charge)

from oscar.apps.offer.models import *  # noqa isort:skip
