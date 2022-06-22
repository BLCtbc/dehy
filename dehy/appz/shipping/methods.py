from oscar.apps.shipping import methods
from oscar.core import prices
from decimal import Decimal as D
from django.utils.translation import gettext_lazy as _

import decimal

decimal.getcontext().prec = 15
TWOPLACES = D(10) ** -2

# https://github.com/django-oscar/django-oscar/blob/master/src/oscar/apps/shipping/methods.py
# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods

class Base(methods.Base):
	arrival = ''
	carrier_code = "fedex"
	def round_two_places(self, value):
		return D(value).quantize(TWOPLACES)

class FreeShipping(methods.FixedPrice, Base):
	code = 'free_shipping'
	name = 'Free Shipping'

	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D('0.00'), incl_tax=D('0.00'))

class FedexGround(methods.FixedPrice, Base):

	code = 'FEDEX_GROUND'
	name = 'FedEx Ground® - FREE For Orders Over $50 (continental US)'

	def calculate(self, basket):
		pp = 5
		if 7.5 > basket.total_weight > 5:
			pp = 12

		elif basket.total_weight > 7.5:
			pp = 15

		return prices.Price(
			currency=basket.currency,
			excl_tax=self.round_two_places(pp), incl_tax=self.round_two_places(pp)
			)

class BaseFedex(methods.FixedPrice, Base):
	def __init__(self, code, name, arrival='', carrier_code="fedex", charge_excl_tax=None, charge_incl_tax=None):
		super().__init__(charge_excl_tax, charge_incl_tax)
		self.code = code
		self.name = name
		self.arrival = arrival
		self.carrier_code = carrier_code

	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=self.round_two_places(self.charge_excl_tax),
			incl_tax=self.round_two_places(self.charge_incl_tax)
			)

class SameDayLocal(methods.FixedPrice, Base):
	code = 'same_day_local'
	name = 'Same Day Local'

	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D('5.00'), incl_tax=D('5.00'))


class TwoDayExpress(Base):
	code = 'two_day'
	name = '2-Day Express'

	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D('20.00'), incl_tax=D(self.round_two_places(20*1.07)))


class NextDayExpress(Base):
	code = 'next_day_standard'
	name = 'Standard Overnight'
	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D(40), incl_tax=D(self.round_two_places(40*1.07)))

