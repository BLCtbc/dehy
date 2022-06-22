from django.urls import path
from . import views

app_name='recipes'
urlpatterns = [
	path('', views.RecipeListView.as_view(), name='browse'),
	path('<slug:recipe_slug>', views.RecipeDetailView.as_view(), name='detail'),
]


