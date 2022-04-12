from django.apps import apps
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_class
import oscar.apps.dashboard.apps as oscar_apps

class DashboardConfig(oscar_apps.DashboardConfig):
	name = 'dehy.appz.dashboard'
	label = 'dashboard'
	verbose_name = _('Dashboard')
	namespace = 'dashboard'
	permissions_map = {
		'index': (['is_staff'], ['partner.dashboard_access']),
	}

	def ready(self):
		super().ready()
		self.recipes_app = apps.get_app_config('recipes_dashboard')
		self.faq_app = apps.get_app_config('faq_dashboard')

	def get_urls(self):
		urls = super().get_urls()
		urls += [
			path('recipes/', include(self.recipes_app.urls[0])),
			path('faq/', include(self.faq_app.urls[0]))
		]
		return self.post_process_urls(urls)