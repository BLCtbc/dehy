import oscar.apps.customer.apps as apps
from oscar.core.loading import get_class
from django.contrib.auth.decorators import login_required
from django.urls import path

class CustomerConfig(apps.CustomerConfig):
	name = 'dehy.appz.customer'

	def ready(self):
		super().ready()

		self.billing_info_view = get_class('customer.views', 'BillingInfoView')


	def get_urls(self):
		urls = super().get_urls()

		urls += [
			path('billing-info/', login_required(self.billing_info_view.as_view()), name='billing-info'),
		]

		return urls