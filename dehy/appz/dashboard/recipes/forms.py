from django import forms
import math
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_model
from django.core.validators import RegexValidator
from django.contrib.postgres.forms import SimpleArrayField, SplitArrayField
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.widgets import DynamicArrayTextareaWidget
from django_better_admin_arrayfield.forms.fields import DynamicArrayField


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
			forms.NumberInput(attrs={'step':'any', 'min':0}),
			forms.Select(choices=self.UNITS_OF_MEASUREMENT_CHOICES),
			forms.TextInput()
		]
		super().__init__(widgets, attrs, *args, **kwargs)

	# only called on update, not create
	def decompress(self, value):
		print(f'\n *** decompressing: {value}')
		if value:
			return value.split(',')
		return ['', '', '']

	def value_from_datadict(self, data, files, name, *args, **kwargs):
		print('\n *** value_from_datadict')
		print(f'\n name {name}')
		print(f'\n pre super*** data {data}')
		print(f'\n dir(self) multiwidget {dir(self)}')
		step = len(self.widgets)

		vals = []

		ingredients = get_ingredients(data, name, step)
		if ingredients:
			vals = ingredients
		else:
			vals = super().value_from_datadict(data, files, name, *args, **kwargs)

		print(f'\n vals: {vals}')
		print('\n end value_from_datadict ***')

		return vals


	# only called on update, not create
	def get_context(self, name, value, attrs):
		value = value or ['']
		print(f'\n ** FORMS get_context value {value}')
		print(f'\n ** FORMS get_context name {name}')

		context = super().get_context(name, value, attrs)

		# print(f'\n ** FORMS get_context {context}')
		return context


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

	def clean(self, value, *args, **kwargs):
		print('\n *** cleaning multivaluefield')
		print(f'\n dir(self) multivaluefield {dir(self)} \n')
		print(f'\n uncleaned value multivaluefield: {value}')
		cleaned_data = super().clean(value, *args, **kwargs)
		print(f'\n cleaned data multivaluefield: {value}')

		cleaned_data['ingredients'] = value
		return cleaned_data

	def compress(self, data_list):
		print(f'\n** compressing ** {data_list}')
		data_list = [str(x) for x in data_list]
		data_list = str(','.join(data_list))
		return data_list

	def __init__(self, *args, **kwargs):
		# Define one message for all fields.
		error_messages = {
			'incomplete': 'Enter ingredient information: quantity, measurement, and name',
		}

		fields = (
			forms.DecimalField(
				label=_('amount'), help_text='quantity', min_value=0, decimal_places=2,
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
			error_messages=error_messages, fields=fields, *args, **kwargs
		)

	def coerce(self, x):
		return str(x)

class RecipeCreateUpdateForm(forms.ModelForm, DynamicArrayMixin):
	name = forms.CharField(label=_('Recipe name'), max_length=50)
	description = forms.CharField(required=False, label=_('Description'), widget=forms.Textarea(attrs={'cols': 40, 'rows': 10}))
	image = forms.ImageField()

	# ingredients = IngredientField()
	# ingredients = SimpleArrayField(SimpleArrayField(forms.CharField(help_text='ingredient name')),delimiter='|')
	ingredients = DynamicArrayField(forms.CharField())

	# ingredients = SplitArrayField(forms.CharField(help_text='ingredient name'), size=3)
	slug = forms.SlugField(label=('Slug'), required=True)
	steps = DynamicArrayField(forms.CharField())


	class Meta:
		model = Recipe
		fields = ['name', 'slug', 'image', 'description', 'ingredients', 'steps', 'featured']


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['ingredients'].widget.attrs.update({'class': 'special'})


def get_ingredients(data, name, step):
	qd = list(data.items())
	vals = []
	for item in qd:
		if name in item[0]:
			vals.append(item[1])

	vals_2d = []
	if len(vals)%step==0:
		num_lists = len(vals)/step
		for i in range(int(num_lists)):
			n = max(min(i * step, math.inf), 0)
			m = ((i+1)*step)
			vals_2d.append(vals[n:m])
		vals = vals_2d

	return vals