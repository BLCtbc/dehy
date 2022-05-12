import oscar.apps.customer.apps as apps
from oscar.core.loading import get_class
from django.contrib.auth.decorators import login_required
from django.urls import path

class CustomerConfig(apps.CustomerConfig):
	name = 'dehy.appz.customer'

	def ready(self):
		super().ready()
		self.billing_list_view = get_class('customer.views', 'BillingListView')
		self.billing_edit_view = get_class('customer.views', 'BillingEditView')
		self.billing_add_view = get_class('customer.views', 'BillingAddView')


	def get_urls(self):
		urls = super().get_urls()

		urls += [
			path('billing/', login_required(self.billing_list_view.as_view()), name='billing'),
			path('billing/edit/', login_required(self.billing_edit_view.as_view()), name='billing-edit'),
			path('billing/add/', login_required(self.billing_add_view.as_view()), name='billing-add'),
		]

		return urls