from django.urls import path
from . import views

urlpatterns = [
	path('recipes/', views.RecipesView.as_view(), name='recipes'),
	path('recipes/<slug:recipe_slug>', views.RecipeDetailView.as_view(), name='recipe_details'),
]


