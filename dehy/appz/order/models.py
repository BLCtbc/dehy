from oscar.apps.order.abstract_models import AbstractOrder
from oscar.apps.address.abstract_models import AbstractBillingAddress
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from dehy.appz.address.models import AbstractAddress
from django.utils.translation import gettext_lazy as _

class Order(AbstractOrder):
	additional_info_questionnaire = models.ForeignKey('generic.AdditionalInfoQuestionnaire',
		on_delete=models.SET_NULL, null=True, blank=True)

	@property
	def total_tax(self):
		return self.total_incl_tax - (self.total_excl_tax + self.shipping_excl_tax)

class BillingAddress(AbstractBillingAddress):
	phone_number = PhoneNumberField(_("Phone number"), blank=True)


from oscar.apps.order.models import *  # noqa isort:skip
