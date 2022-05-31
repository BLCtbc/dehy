from oscar.apps.offer import benefits, conditions, models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal as D
from oscar.core.loading import get_class, get_model
from oscar.templatetags.currency_filters import currency

unit_price = get_class('offer.utils', 'unit_price')
Range = get_model('offer', 'Range')
ApplicationResult = get_class('offer.results', 'ApplicationResult')
all_products_range = Range.objects.get(name='All Products')

class ShippingDiscount(ApplicationResult):
	"""
	For when an offer application leads to a discount from the shipping cost
	"""
	def __init__(self, amount):
		self.discount = amount

	is_successful = is_final = True
	affects = ApplicationResult.SHIPPING

class FreeFedexGroundShippingCondition(conditions.ValueCondition):
	name = "Free Fedex Ground shipping for orders over $50"
	description = "Shipping method must be fedex_ground and value of order must exceed $50"

	class Meta:
		proxy = True
		verbose_name = _("Shipping method value condition")
		verbose_name_plural = _("Shipping method value conditions")

	def is_satisfied(self, offer, basket):
		value_of_matches = D('0.00')
		satisfied = False
		for line in basket.all_lines():
			if (self.can_apply_condition(line) and line.quantity_without_offer_discount(offer) > 0):
				price = unit_price(offer, line)
				value_of_matches += price * int(line.quantity_without_offer_discount(offer))
			if value_of_matches >= self.value:
				satisfied = True


		if not satisfied or not basket.shipping_method_code:
			return False

		satisfied = basket.shipping_method_code.lower()=='fedex_ground'
		return basket.shipping_method_code.lower() == 'fedex_ground'

	def get_upsell_message(self, offer, basket):
		value_of_matches = self._get_value_of_matches(offer, basket)
		delta = self.value - value_of_matches
		if delta > 0:
			return _('Spend %(value)s more to get free shipping!') % {'value': currency(delta, basket.currency)}

class FreeGroundShippingBenefit(benefits.ShippingPercentageDiscountBenefit):
	_description = _("%(value)s%% off of shipping cost")

	class Meta:
		app_label = 'offer'
		proxy = True
		verbose_name = _("100% off ground shipping discount benefit")
		verbose_name_plural = _("100% off ground shipping discount benefits")

	@property
	def description(self):
		return self._description

	@property
	def name(self):
		return self._description % {'value': self.value}

	# def apply(self, basket, condition, offer, **kwargs):
	# 	print('applying, ', kwargs)
	# 	print('dir(self): ', dir(self))
	# 	condition.consume_items(offer, basket, affected_lines=())
	# 	return ShippingDiscount(self.shipping_discount())

	def shipping_discount(self, charge, currency=None):
		discount = charge * self.value / D('100.0')
		return discount.quantize(D('0.01'))