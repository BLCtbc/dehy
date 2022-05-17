import oscar.apps.customer.apps as apps
from oscar.core.loading import get_class
from django.contrib.auth.decorators import login_required
from django.urls import path

class CustomerConfig(apps.CustomerConfig):
	name = 'dehy.appz.customer'

	def ready(self):
		super().ready()
		self.payment_list_view = get_class('customer.views', 'PaymentMethodListView')
		self.payment_edit_view = get_class('customer.views', 'PaymentMethodEditView')
		self.payment_add_view = get_class('customer.views', 'PaymentMethodAddView')
		self.verification_view = get_class('customer.views', 'VerificationView')


	def get_urls(self):
		urls = super().get_urls()

		urls += [
			path('payment/', login_required(self.payment_list_view.as_view()), name='payment'),
			path('payment/edit/<card_id>', login_required(self.payment_edit_view.as_view()), name='payment-edit'),
			path('payment/add/', login_required(self.payment_add_view.as_view()), name='payment-add'),
			# path('verification/', self.verification_view.as_view(), name='verification'),
			path('verify/<uidb64>/<token>', self.verification_view.as_view(), name='verification')

		]

		return urls