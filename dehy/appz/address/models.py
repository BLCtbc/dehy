from oscar.apps.address.abstract_models import AbstractAddress as BaseAbstractAddress
from oscar.apps.address.abstract_models import AbstractUserAddress

from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from . import us_states

class AbstractAddress(BaseAbstractAddress):
	city = models.CharField(_("City"), max_length=255, blank=True)

class UserAddress(AbstractUserAddress):
	knickname = models.CharField(_("Label"), max_length=120, blank=True, help_text=_("Add a label or knickname for this address"))
	notes = models.TextField(_("Notes"), max_length=500, blank=True, help_text=_("Add delivery instructions/notes, such as preferred delivery times and dates. NOTE: only applies to Austin metro area"))

	hash_fields = ['salutation', 'line1', 'line2', 'line3', 'line4', 'state', 'postcode', 'country']
	base_fields = ['salutation', 'line1', 'line2', 'line3', 'line4', 'state', 'postcode', 'country', 'notes', 'knickname']

	def save(self, *args, **kwargs):
		if self.country.iso_3166_1_a2=='US' and len(self.state)>2:
			self.state = self.coerce_state_value(self.state)
		super().save(*args, **kwargs)

	def coerce_state_value(self, state_val):
		st = state_val.upper()
		if st in us_states.keys():
			st = us_states[state_val]
		return st


from oscar.apps.address.models import *  # noqa isort:skip
