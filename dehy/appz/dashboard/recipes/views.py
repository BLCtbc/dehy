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
RecipesTable = get_class('dashboard.recipes.tables', 'RecipesTable')

class RecipeListView(SingleTableView):
	"""
	Dashboard view of the recipe list.
	Supports the permission-based dashboard.
	"""

	model = Recipe
	template_name = 'dehy/dashboard/recipes/recipe_list.html'
	# context_object_name = "recipe_list"
	context_table_name = 'recipes'
	table_class = RecipesTable
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

	def get_context_data(self, **kwargs):
		context_data = super().get_context_data(**kwargs)
		context_data['title'] = _('Create new recipe')
		form = context_data['form']
		return context_data

	def forms_invalid(self, form, inlines):
		messages.error(self.request, "Your submitted data was not valid - please correct the below errors")
		return super().forms_invalid(form, inlines)

	def forms_valid(self, form, inlines):
		# form.instance.creator = self.request.user
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
		context_data = super().get_context_data(**kwargs)
		context_data['title'] = self.object.name
		print(f'\n** VIEWS get_context_data: {context_data}')

		return context_data

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