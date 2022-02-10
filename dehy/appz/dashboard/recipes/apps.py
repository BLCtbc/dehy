from oscar.core.application import OscarDashboardConfig
from django.urls import path
from oscar.core.loading import get_class
import oscar.apps.catalogue.apps as apps
from django.utils.translation import gettext_lazy as _

class RecipesDashboardConfig(OscarDashboardConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'dehy.appz.dashboard.recipes'
	label = 'recipes_dashboard'
	verbose_name = _('Recipes')
	# namespace = 'recipes'
	default_permissions = ['is_staff']
	permissions_map = _map = {
        'recipe-create': (['is_staff'],
                                     ['partner.dashboard_access']),
        'recipe-list': (['is_staff'], ['partner.dashboard_access']),
        'recipe-delete': (['is_staff'],
                                     ['partner.dashboard_access']),
        'recipe-update': (['is_staff'],
                                     ['partner.dashboard_access']),
    }


	def ready(self):
		super().ready()
		self.recipes_list_view = get_class('dashboard.recipes.views', 'RecipeListView')
		self.recipes_create_view = get_class('dashboard.recipes.views', 'RecipeCreateView')
		self.recipes_update_view = get_class('dashboard.recipes.views', 'RecipeUpdateView')
		self.recipes_delete_view = get_class('dashboard.recipes.views', 'RecipeDeleteView')

	def get_urls(self):
		urls = super().get_urls()
		urls += [
			path('', self.recipes_list_view.as_view(), name='recipe-list'),
			path('create/', self.recipes_create_view.as_view(), name='recipe-create'),
			path('update/<int:pk>/', self.recipes_update_view.as_view(), name='recipe-update'),
			path('delete/<int:pk>/', self.recipes_delete_view.as_view(), name='recipe-delete'),
		]
		return self.post_process_urls(urls)
