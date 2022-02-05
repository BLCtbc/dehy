from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from oscar.core.loading import get_class, get_model
from django_tables2 import SingleTableView

Recipe = get_model('recipes', 'Recipe')

RecipeCreateUpdateForm = get_class('dashboard.recipes.forms', 'RecipeCreateUpdateForm')
RecipeSearchForm = get_class('dashboard.recipes.forms', 'RecipeSearchForm')

class RecipeListView(generic.ListView):
	"""
	Dashboard view of the recipe list.
	Supports the permission-based dashboard.
	"""

	model = Recipe
	template_name = 'dehy/dashboard/recipes/recipe_list.html'
	context_object_name = "recipe_list"
	context_table_name = 'recipes'
	paginate_by = 20
	filterform_class = RecipeSearchForm
	form_class = RecipeSearchForm


	def get_title(self):
		data = getattr(self.filterform, 'cleaned_data', {})
		name = data.get('name', None)
		ingredients = data.get('ingredients', None)
		if name and not ingredients:
			return gettext('Recipes matching "%s"') % (name)
		elif name and ingredients:
			return gettext('Recipes matching "%s" containing "%s"') % (name, ingredients)
		elif ingredients:
			return gettext('Recipes containing "%s"') % (ingredients)
		else:
			return gettext('Recipes')

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		data['filterform'] = self.filterform
		data['queryset_description'] = self.get_title()
		return data

	def get_queryset(self):
		qs = self.model.objects.all()
		self.filterform = self.filterform_class(self.request.GET)
		if self.filterform.is_valid():
			qs = self.filterform.apply_filters(qs)
		return qs

class RecipeCreateView(generic.CreateView):
	model = Recipe
	template_name = 'dehy/dashboard/recipes/recipe_update.html'
	form_class = RecipeCreateUpdateForm
	success_url = reverse_lazy('dashboard:recipe-list')

	# def get(self, *args, **kwargs):
	# 	form = self.form_class(self.request.GET)
	# 	print(f'form.is_valid: {form.is_valid()}')
	# 	# response = super().post(*args, **kwargs)
	# 	print(f'\n *** GET ')
	#
	# 	response = render(self.request, self.template_name, context=self.get_context_data())
	# 	return response

	def get_context_data(self, **kwargs):
		context_data = super().get_context_data(**kwargs)
		context_data['title'] = _('Create new recipe')
		print(f'\n context_data: {context_data}')
		form = context_data['form']
		print(f'\n form {dir(form)}')
		print(f'\n form {form.fields}')
		print(f'\n form {form.fields["ingredients"]}')
		print(f'\n dir ingredients {dir(form.fields["ingredients"])}')
		print(f'\n widget {form.fields["ingredients"].widget}')
		print(f'\n type(fields) {type(form.fields["ingredients"].fields)}')

		return context_data

	def forms_invalid(self, form, inlines):
		print(f'\n *** forms_invalid ')
		messages.error(self.request, "Your submitted data was not valid - please correct the below errors")
		return super().forms_invalid(form, inlines)

	def forms_valid(self, form, inlines):
		print(f'\n *** forms_valid ')
		response = super().forms_valid(form, inlines)
		msg = render_to_string('oscar/dashboard/recipes/messages/recipe_saved.html', {'recipe': self.object})
		messages.success(self.request, msg, extra_tags='safe')
		return response

class RecipeUpdateView(generic.UpdateView):
	model = Recipe
	template_name = "dehy/dashboard/recipes/recipe_update.html"
	form_class = RecipeCreateUpdateForm
	success_url = reverse_lazy('dashboard:recipe-list')


	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['title'] = self.object.name
		return ctx

	def forms_invalid(self, form, inlines):
		messages.error(
			self.request,
			"Your submitted data was not valid - please correct the below errors")
		return super().forms_invalid(form, inlines)

	def forms_valid(self, form, inlines):
		msg = render_to_string('dehy/dashboard/recipes/messages/recipe_saved.html',
							   {'recipe': self.object})
		messages.success(self.request, msg, extrforms_valida_tags='safe')
		return super().forms_valid(form, inlines)

class RecipeDeleteView(generic.DeleteView):
	model = Recipe
	template_name = "dehy/dashboard/recipes/recipe_delete.html"
	success_url = reverse_lazy('dashboard:recipe-list')