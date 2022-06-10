from oscar.apps.order.abstract_models import AbstractOrder
from oscar.apps.address.abstract_models import AbstractBillingAddress, AbstractShippingAddress
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from dehy.appz.address.models import AbstractAddress
from django.utils.translation import gettext_lazy as _

class Order(AbstractOrder):
	questionnaire = models.ForeignKey('generic.AdditionalInfoQuestionnaire',
		on_delete=models.SET_NULL, null=True, blank=True)

	@property
	def total_tax(self):
		return self.total_incl_tax - (self.total_excl_tax + self.shipping_excl_tax)

	def save(self, *args, **kwargs):
		if self.basket and self.basket.questionnaire:
			self.questionnaire = self.basket.questionnaire
			
		super().save(*args, **kwargs)

class BillingAddress(AbstractBillingAddress):
	phone_number = PhoneNumberField(_("Phone number"), blank=True)

class ShippingAddress(AbstractShippingAddress):
	is_residential = models.BooleanField(default=True)
	is_validated = models.BooleanField(default=False)


	def save(self, *args, **kwargs):

		if not self.is_validated:
			# TODO: add a method here that corrects various fields of a shipping addresses before they are
			# saved using a function similar to validate_address from repository
			pass

		super().save(*args, **kwargs)



from oscar.apps.order.models import *  # noqa isort:skip
