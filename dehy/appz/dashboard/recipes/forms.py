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
		# widgets = [
		# 	forms.TextInput(),
		# 	forms.TextInput(),
		# 	forms.TextInput()
		# ]

		# old
		widgets = [
			forms.TextInput(attrs={'step':'any', 'min':0}),
			forms.Select(choices=self.UNITS_OF_MEASUREMENT_CHOICES),
			forms.TextInput()
		]
		super().__init__(widgets, attrs, *args, **kwargs)

	def decompress(self, value):
		print(f'\n *** decompressing: {value}')

		if value:
			return value.split(',')
		return ['', '', '']

	# def value_from_datadict(self, data, files, name):
	# 	# print(f'\n dir(MultiWidget): {dir(self)}')
	# 	# print(f'\n self.widgets: {self.widgets}')
	#
	#
	# 	vals = super().value_from_datadict(data, files, name)
	# 	print(f'** value_from_datadict: {vals} **')
	#
	# 	# DateField expects a single string that it can parse into a date.
	# 	# print(f'\n a: {a}')
	# 	# print(f'\n b: {b}')
	# 	# print(f'\n c: {c}')
	#
	# 	return vals

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
	#
	# def clean(self, *args, **kwargs):
	# 	print('\n cleaning multivaluefield \n')
	# 	print(f'\n dir(self) multivaluefield {dir(self)} \n')
	# 	print(f'errors: {self.error_messages}')
	#
	# 	# cleaned_data = super().clean(*args, **kwargs)
	# 	cleaned_data = self.compress(*args, **kwargs)
	#
	# 	print('\nMultiValueField cleaned_data: ', cleaned_data)
	# 	return cleaned_data
	#
	# def to_python(self, *args, **kwargs):
	# 	print(f'\n** to_python {val} \n')
	# 	val = super().to_python(*args, **kwargs)
	# 	return val
	#
	#
	# def validate(self, *args, **kwargs):
	# 	print('\n** validate() \n')
	# 	pass
	#
	# def run_validators(self, *args, **kwargs):
	# 	print('\n** run_validators() \n')
	# 	# super().run_validators(*args, **kwargs)

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
		# Or define a different message for each field.
		# fields = (
		# 	forms.CharField(
		# 		label=_('amount'), help_text='quantity',
		# 	),
		# 	forms.CharField(
		# 		label=_('Unit of measurement'), help_text='Unit of measurement, eg. mL, oz',
		# 	),
		# 	forms.CharField(
		# 		help_text='ingredient name',
		# 	),
		# )

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

class RecipeCreateUpdateForm(forms.ModelForm):
	name = forms.CharField(label=_('Recipe name'), max_length=50)
	description = forms.CharField(required=False, label=_('Description'), widget=forms.Textarea(attrs={'cols': 40, 'rows': 10}))
	ingredients = IngredientField()
	# ingredients = SplitArrayField(forms.CharField(help_text='ingredient name'), size=3)
	slug = forms.SlugField(label=('Slug'), required=False)
	steps = SimpleArrayField(forms.CharField(help_text='directions'), delimiter='|')

	prepopulated_fields = {"slug": ("name",)}

	def clean(self):

		cleaned_data = super().clean()
		if 'ingredients' in cleaned_data.keys():
			cleaned_data['ingredients'] = [cleaned_data['ingredients'].split(',')]

		return cleaned_data

	# def full_clean(self):

	class Meta:
		model = Recipe
		fields = ['name', 'slug', 'description', 'ingredients', 'steps']


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		print(f"\n form.is_valid() {self.is_valid()}")
		print(f"\n form.errors {self.errors}")
		print(f"\n form.non_field_errors {self.non_field_errors()}")


		# print(f'\n ** form dir(self) {dir(self)}\n')

		self.fields['ingredients'].widget.attrs.update({'class': 'special'})
		
		print(f'\n form {self.fields["ingredients"]}')
		print(f'\n dir ingredients {dir(self.fields["ingredients"])}')
		print(f'\n widget {self.fields["ingredients"].widget}')
		print(f'\n type(fields) {type(self.fields["ingredients"].fields)}')