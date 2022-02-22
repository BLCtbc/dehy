from oscar.apps.shipping import methods
from oscar.core import prices
from decimal import Decimal as D
# https://github.com/django-oscar/django-oscar/blob/master/src/oscar/apps/shipping/methods.py
# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods

class Standard(methods.Base):
	code = 'standard'
	name = 'Standard shipping (free)'

	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D('0.00'), incl_tax=D('0.00'))

class Express(methods.FixedPrice):
	code = 'express'
	name = 'Express shipping'
	charge_excl_tax = D('10.00')


	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D('0.00'), incl_tax=D('0.00'))