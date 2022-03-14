from oscar.apps.address.abstract_models import AbstractAddress as BaseAbstractAddress
from django.db import models
from django.utils.translation import gettext_lazy as _

class AbstractAddress(BaseAbstractAddress):

	city = models.CharField(_("City"), max_length=255, blank=True)

from oscar.apps.address.models import *  # noqa isort:skip
