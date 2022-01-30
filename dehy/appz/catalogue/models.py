# dehy/apps/catalogue/models.py
from django.template.defaultfilters import striptags
from django.db import models
from datetime import datetime
from django.urls import reverse
from oscar.models.fields.slugfield import SlugField
from oscar.apps.catalogue.abstract_models import AbstractCategory, AbstractProduct
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
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# print(dir(self))
		# if self.parent:
		# 	print(f'self.parent: {self.parent}')
		# 	self.Meta.order_with_respect_to = 'parent'

		# print(self.Meta.ordering)

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

		super().save(*args, **kwargs)

	def get_lowest_variant(self):
		if self.structure=='child':
			# self.children.objects.all().aggregate(Max('price'))
			# self.children.aggregate(Min('stockrecords__price'))
			lowest = parent.children.aggregate(lowest=models.Min('stockrecords__price'))['lowest']
			print(f'lowest price: {lowest}')
			return parent.children.aggregate(lowest=models.Min('stockrecords__price'))['lowest']

	@property
	def lowest(self):
		return self.get_lowest_variant()

	def get_absolute_url(self):
		"""
		Return a product's absolute URL
		"""
		return f"{reverse('catalogue:detail', kwargs={'product_slug': self.slug})}"

	class Meta:
		order_with_respect_to = 'parent'
		# ordering = [models.F('parent').asc(nulls_last=True)]



class Category(AbstractCategory):
	slug = SlugField(_('Slug'), max_length=255, db_index=True, unique=True)

	def get_url_cache_key(self):
		current_locale = get_language()
		cache_key = 'CATEGORY_URL_%s_%s' % (current_locale, self.slug)
		return

	def _get_absolute_url(self, parent_slug=None):
		"""
		Our URL scheme means we have to look up the category's ancestors. As
		that is a bit more expensive, we cache the generated URL. That is
		safe even for a stale cache, as the default implementation of
		ProductCategoryView does the lookup via primary key anyway. But if
		you change that logic, you'll have to reconsider the caching
		approach.
		"""

		return reverse('catalogue:category', kwargs={
			'category_slug': self.get_full_slug(parent_slug=parent_slug)
		})

from oscar.apps.catalogue.models import *