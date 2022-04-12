from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Recipe

# class RecipesView(TemplateView):
# 	template_name = "dehy/recipes/recipes.html"

class RecipeListView(ListView):
	model = Recipe
	context_object_name = "recipes"
	template_name = "dehy/recipes/recipes.html"


	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)
		return context_data


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "dehy/recipes/detail.html"
    context_object_name = "recipe"
    slug_field = 'slug'
    slug_url_kwarg = 'recipe_slug'
