from django import forms
from dehy.appz.catalogue.models import Product
from oscar.apps.dashboard.catalogue import forms as base_forms

class ProductForm(base_forms.ProductForm):

	class Meta(base_forms.ProductForm.Meta):
		model = Product
		fields = [
			'title', 'upc', 'description', 'length', 'width', 'height', 'weight', 'is_public', 'featured',
			'is_discountable', 'structure', 'slug', 'meta_title',
			'meta_description'
		]
		widgets = {
			'structure': forms.HiddenInput(),
			'meta_description': forms.Textarea(attrs={'class': 'no-widget-init'})
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		parent = kwargs.get('parent', None)
		instance = kwargs.get('instance', None)

		if not parent and (instance and instance.structure != 'standalone'):
			self.delete_variant_shipping_fields()

	def delete_variant_shipping_fields(self):
		"""
		Removes any fields not needed for parent class, e.g variant-specific fields needed
		for shipping, weight/dimensions, etc.
		"""
		for field_name in ['weight', 'length', 'width', 'height']:
			if field_name in self.fields:
				del self.fields[field_name]