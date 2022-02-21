from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Recipe

# class RecipesView(TemplateView):
# 	template_name = "dehy/recipes/recipes.html"

class RecipeListView(ListView):
	model = Recipe
	context_object_name = "recipes"
	template_name = "dehy/recipes/recipes.html"

	# def get(self, request, *args, **kwargs):
		# test_recipes = {
		# 	'bourbon_old_fashion': {
		# 		'name': 'Bourbon Old Fashioned', 'description': 'Start by using good bourbon, the rule being that if you wouldn’t sip it by itself it has no place at the helm of a Bourbon Old Fashioned. (There are other whiskey drinks for masking subpar booze—this isn’t one of them.) From there, the cocktail-minded seem to break into two camps: simple syrup or muddled sugar.',
		# 		'ingredients': ['1/2 teaspoon sugar', '3 dashes Angostura bitters', '1 teaspoon water', '2 ounces bourbon', 'Garnish: orange peel'],
		# 		'steps': ['Add the sugar and bitters to a rocks glass, then add the water, and stir until the sugar is nearly dissolved.', 'Fill the glass with large ice cubes, add the bourbon, and gently stir to combine.','Express the oil of an orange peel over the glass, then drop in.'],
		# 		'slug': 'bourbon-old-fashioned'
		# 	}
			# 'dirty_martini': {
			# 	'name':'Dirty Martini', 'featured':True, 'slug':'dirty-martini',
			# 	'steps':['Add the gin or vodka, vermouth and olive brine to a mixing glass filled with ice and stir until well-chilled.',
			# 		'Strain into a chilled cocktail glass.', 'Garnish with a skewer of olives.'],
			# 	'ingredients': ['2 1/2 ounces gin or vodka', '1/2 ounce dry vermouth', '1/2 ounce olive brine', 'Garnish: 2 to 4 olives'],
			# 	'description': 'The classic Dry Martini is the standard bearer among recipes and variations, but countless riffs take the drink in new directions, from the 50/50 Martini, which combines equals parts gin and dry vermouth, to the Perfect Martini, which splits the vermouth between sweet and dry. There are also countless ’tinis, often sugary, neon-colored drinks served in stemmed glasses that are another category of drink. (For this exercise, those don’t count.) And then you have the savory, beguiling and controversial Dirty Martini.'
			# }
		# }


		# for val in test_recipes.values():
		# 	recipe,_ = Recipe.objects.update_or_create(
		# 		name=val['name'], slug=val['slug'],
		# 		featured=True,
		# 		ingredients=val['ingredients'],
		# 		steps=val['steps'],
		# 		description=val['description']
		# 	)
		#
		# 	recipe.save()

		# super().get(request, *args, **kwargs)


	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)


		return context_data


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "dehy/recipes/detail.html"
    context_object_name = "recipe"
    slug_field = 'slug'
    slug_url_kwarg = 'recipe_slug'
