from oscar.apps.shipping import methods
from oscar.core import prices
from decimal import Decimal as D
import decimal

decimal.getcontext().prec = 15
# https://github.com/django-oscar/django-oscar/blob/master/src/oscar/apps/shipping/methods.py
# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods
class Base(methods.Base):
	def convert_to_currency(self, value):
		return f'{int(value)}.{round((value - int(value)) * 100)}'

class Standard(Base):

	code = 'standard_ground'
	name = 'Standard Ground'

	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D('15.00'), incl_tax=D('15.00'))

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
			excl_tax=D('20.00'), incl_tax=D(self.convert_to_currency(20*1.07)))


class NextDayExpress(Base):
	code = 'next_day_standard'
	name = 'Standard Overnight'
	def calculate(self, basket):
		return prices.Price(
			currency=basket.currency,
			excl_tax=D(40), incl_tax=D(self.convert_to_currency(40*1.07)))

