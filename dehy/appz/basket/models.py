from oscar.apps.basket.abstract_models import AbstractBasket, AbstractLine
from django.db import models
from django.utils.translation import gettext_lazy as _

from oscar.core.loading import get_class

Unavailable = get_class('partner.availability', 'Unavailable')

class Basket(AbstractBasket):
	payment_intent_id = models.CharField(max_length=255, help_text='Payment Intent ID(Stripe)', blank=True, null=True)
	stripe_customer_id = models.CharField(max_length=255, help_text='Stripe Customer ID', blank=True, null=True)
	stripe_order_id = models.CharField(max_length=255, help_text='Stripe Order ID', blank=True, null=True)
	stripe_order_status = models.CharField(max_length=50, help_text='Stripe Order Status', blank=True, null=True)
	payment_intent_client_secret = models.CharField(max_length=255, help_text='Payment Intent Client Secret (Stripe)', blank=True, null=True)
	stripe_order_client_secret = models.CharField(max_length=255, help_text='Order Client Secret (Stripe)', blank=True, null=True)

	@property
	def total_weight(self):
		return sum([line.get_weight for line in self.lines.all()])

class Line(AbstractLine):


	price_incl_tax = models.DecimalField(_('Price incl. Tax'), decimal_places=5, max_digits=12, null=True)

	@property
	def get_weight(self):
		return self.product.weight*self.quantity

	def get_warning(self):
		"""
		Return a warning message about this basket line if one is applicable
		This could be things like the price has changed
		"""
		if isinstance(self.purchase_info.availability, Unavailable):
			msg = "'%(product)s' is no longer available"
			return _(msg) % {'product': self.product.get_title()}

		if not self.price_incl_tax:
			return
		if not self.purchase_info.price.is_tax_known:
			return

		return

		############################
		### This part of the function is generating "price increased" warnings after tax is calculated,
		### likely erroneous. Informing the customer of price increases seems like poor business practice.
		############################

		# Compare current price to price when added to basket
		# current_price_incl_tax = self.purchase_info.price.incl_tax

		# if current_price_incl_tax != self.price_incl_tax:
		#     product_prices = {
		#         'product': self.product.get_title(),
		#         'old_price': currency(self.price_incl_tax, self.price_currency),
		#         'new_price': currency(current_price_incl_tax, self.price_currency)
		#     }
		#     if current_price_incl_tax > self.price_incl_tax:
		#         warning = _("The price of '%(product)s' has increased from"
		#                     " %(old_price)s to %(new_price)s since you added"
		#                     " it to your basket")
		#         return warning % product_prices
		#     else:
		#         warning = _("The price of '%(product)s' has decreased from"
		#                     " %(old_price)s to %(new_price)s since you added"
		#                     " it to your basket")
		#         return warning % product_prices

from oscar.apps.basket.models import *