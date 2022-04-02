from oscar.apps.address.abstract_models import AbstractAddress as BaseAbstractAddress
from oscar.apps.address.abstract_models import AbstractBillingAddress

from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

class AbstractAddress(BaseAbstractAddress):
	city = models.CharField(_("City"), max_length=255, blank=True)


from oscar.apps.address.models import *  # noqa isort:skip
