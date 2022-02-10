from django.urls import path
from . import views

urlpatterns = [
	path('', views.RecipeListView.as_view(), name='recipes'),
	path('<slug:recipe_slug>', views.RecipeDetailView.as_view(), name='recipe_details'),
]


