from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_model
from django.core.validators import RegexValidator
from django.contrib.postgres.forms import SimpleArrayField, SplitArrayField

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

class IngredientWidget(forms.MultiWidget):
	UNITS_OF_MEASUREMENT_CHOICES = (
		('oz', 'ounces'),
		('tsp', 'teaspoons'),
		('tbsp', 'tablespoons'),
		('cup', 'cups'),
		('qt', 'quarts'),
		('gal', 'gallons'),
		('lb', 'pounds'),
		# metric
		('mL', 'millileters'),
		('g', 'grams'),
		('L', 'liters'),
		('kg', 'kilograms'),
	)

	def __init__(self, attrs=None, *args, **kwargs):
		attrs={'class': 'special'}
		widgets = [
			forms.NumberInput(attrs={'step':'any'}),
			forms.Select(choices=self.UNITS_OF_MEASUREMENT_CHOICES),
			forms.TextInput()
		]
		super().__init__(widgets, attrs, *args, **kwargs)

	def decompress(self, value):
		print(f'decompressing: {value}')
		if value:
			return value.split(',')
		return ['', '', '']

class IngredientField(forms.MultiValueField):
	widget = IngredientWidget()
	UNITS_OF_MEASUREMENT_CHOICES = (
		('oz', 'ounces'),
		('tsp', 'teaspoons'),
		('tbsp', 'tablespoons'),
		('cup', 'cups'),
		('qt', 'quarts'),
		('gal', 'gallons'),
		('lb', 'pounds'),
		# metric
		('mL', 'millileters'),
		('g', 'grams'),
		('L', 'liters'),
		('kg', 'kilograms'),
	)

	def compress(self, data_list):
		print('compressing: data list: ', data_list)
		data_list = [str(x) for x in data_list]
		v = str(','.join(data_list))
		print('compressed: ', v)
		return str(v)

	def __init__(self, **kwargs):
		# Define one message for all fields.
		error_messages = {
			'incomplete': 'Enter ingredient information: quantity, measurement, & name',
		}
		# Or define a different message for each field.
		fields = (
			forms.DecimalField(
				label=_('amount'), min_value=0, decimal_places=2, help_text='quantity',
				error_messages={'incomplete': 'Enter an amount.'},
			),
			forms.TypedChoiceField(
				label=_('Unit of measurement'), help_text='Unit of measurement, eg. mL, oz',
				coerce=self.coerce, choices=self.UNITS_OF_MEASUREMENT_CHOICES,
				error_messages={'incomplete': 'Enter valid unit of measurement'},
			),
			forms.CharField(
				help_text='ingredient name',
			),
		)

		super().__init__(
			error_messages=error_messages, fields=fields,
			require_all_fields=True, **kwargs
		)

	def coerce(self, x):
		return str(x)

class RecipeCreateUpdateForm(forms.ModelForm):
	name = forms.CharField(label=_('Recipe name'), max_length=50)
	description = forms.CharField(required=False, label=_('Description'), widget=forms.Textarea(attrs={'cols': 40, 'rows': 10}))
	# ingredients = IngredientField()
	ingredients = SplitArrayField(forms.CharField(help_text='ingredient name'), size=3)
	slug = forms.SlugField(label=('Slug'), required=False)
	steps = SimpleArrayField(forms.CharField(help_text='ingredient name'), delimiter='|')

	prepopulated_fields = {"slug": ("name",)}

	class Meta:
		model = Recipe
		fields = ['name', 'slug', 'description', 'ingredients', 'steps']


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['ingredients'].widget.attrs.update({'class': 'special'})