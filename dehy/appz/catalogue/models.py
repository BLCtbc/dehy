# dehy/appz/catalogue/models.py

from django.template.defaultfilters import striptags
from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct
from django.utils.translation import gettext_lazy as _

class Product(AbstractProduct):

	length = models.FloatField(_('Length'), help_text=_("inches"), null=True, blank=True, default=None)
	width = models.FloatField(_('Width'), help_text=_("inches"), null=True, blank=True, default=None)
	height = models.FloatField(_('Height'), help_text=_("inches"), null=True, blank=True, default=None)
	weight = models.FloatField(_('Weight'), help_text=_("lbs"), null=True, blank=True, default=None)

	meta_description = models.TextField(_('Meta description'), help_text='Leave blank to copy product description',
		blank=True, null=True
	)
	meta_title = models.CharField(_('Meta title'), help_text='Leave blank to copy product title',
		max_length=255, blank=True, null=True
	)

	def save(self, *args, **kwargs):
		# attempt to create
		if not self.meta_description:
			if self.description:
				self.meta_description = striptags(self.description)

			elif self.is_child:
				self.meta_description = self.parent.get_meta_description().strip()

		if not self.meta_title:
			if self.title:
				self.meta_title = self.get_title()

			elif self.is_child:
				self.meta_title = self.parent.get_title()



from oscar.apps.catalogue.models import *  # noqa isort:skip
