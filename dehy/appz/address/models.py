from oscar.apps.address.abstract_models import AbstractAddress as BaseAbstractAddress
from oscar.apps.address.abstract_models import AbstractUserAddress


from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

class AbstractAddress(BaseAbstractAddress):
	city = models.CharField(_("City"), max_length=255, blank=True)

class UserAddress(AbstractUserAddress):
	knickname = models.CharField(_("Label"), max_length=120, blank=True, help_text=_("Add a label or knickname for this address"))
	notes = models.TextField(_("Notes"), max_length=500, blank=True, help_text=_("Add delivery instructions/notes, such as preferred delivery times and dates. NOTE: only applies to Austin metro area"))

	hash_fields = ['salutation', 'line1', 'line2', 'line3', 'line4', 'state', 'postcode', 'country']
	base_fields = ['salutation', 'line1', 'line2', 'line3', 'line4', 'state', 'postcode', 'country', 'notes', 'knickname']

from oscar.apps.address.models import *  # noqa isort:skip
