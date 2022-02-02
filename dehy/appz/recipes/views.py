from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Recipe

class RecipesView(TemplateView):
	template_name = "dehy/recipes.html"

class RecipeListView(ListView):
	model = Recipe
	context_object_name = "recipes"
	# template_name = "dehy/recipes.html"

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "dehy/recipes.html"
    context_object_name = "recipe"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
