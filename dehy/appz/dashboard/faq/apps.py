from oscar.core.application import OscarDashboardConfig
from django.urls import path
from oscar.core.loading import get_class
import oscar.apps.catalogue.apps as apps
from django.utils.translation import gettext_lazy as _

class FAQDashboardConfig(OscarDashboardConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'dehy.appz.dashboard.faq'
	label = 'faq_dashboard'
	verbose_name = _('FAQ')
	default_permissions = ['is_staff']
	permissions_map = _map = {
        'faq-create': (['is_staff'],
                                     ['partner.dashboard_access']),
        'faq-list': (['is_staff'], ['partner.dashboard_access']),
        'faq-delete': (['is_staff'],
                                     ['partner.dashboard_access']),
        'faq-update': (['is_staff'],
                                     ['partner.dashboard_access']),
    }


	def ready(self):
		super().ready()
		self.faq_list_view = get_class('dashboard.faq.views', 'FAQListView')
		self.faq_create_view = get_class('dashboard.faq.views', 'FAQCreateView')
		self.faq_update_view = get_class('dashboard.faq.views', 'FAQUpdateView')
		self.faq_delete_view = get_class('dashboard.faq.views', 'FAQDeleteView')

	def get_urls(self):
		urls = super().get_urls()
		urls += [
			path('', self.faq_list_view.as_view(), name='faq-list'),
			path('create/', self.faq_create_view.as_view(), name='faq-create'),
			path('update/<int:pk>/', self.faq_update_view.as_view(), name='faq-update'),
			path('delete/<int:pk>/', self.faq_delete_view.as_view(), name='faq-delete'),
		]
		return self.post_process_urls(urls)
