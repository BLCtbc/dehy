from django.apps import AppConfig


class RecipesConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'dehy.appz.recipes'
	namespace = 'recipes'
	label = 'recipes'
