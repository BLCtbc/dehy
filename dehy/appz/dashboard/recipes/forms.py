from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_model

Recipe = get_model('recipes', 'Recipe')

class RecipeSearchForm(forms.Form):

	name = forms.CharField(label=_('Recipe name'), required=False)
	ingredients = forms.CharField(label=_('Ingredients list'), required=False)
	slug = forms.SlugField(label=('Slug'), required=False)

	def is_empty(self):
		d = getattr(self, 'cleaned_data', {})
		def empty(key): return not d.get(key, None)
		return empty('name') and empty('ingredients')

	def apply_ingredient_filter(self, qs, value):
		words = value.replace(',', ' ').split()
		q = [Q(city__icontains=word) for word in words]
		return qs.filter(*q)

	def apply_name_filter(self, qs, value):
		return qs.filter(name__icontains=value)

	def apply_filters(self, qs):
		for key, value in self.cleaned_data.items():
			if value:
				qs = getattr(self, 'apply_%s_filter' % key)(qs, value)
		return qs

class RecipeCreateUpdateForm(forms.ModelForm):
	class Meta:
		model = Recipe
		fields = ('name', 'slug', 'ingredients')