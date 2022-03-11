import oscar.apps.checkout.apps as apps
from django.utils.translation import gettext_lazy as _
from django.urls import include, path
from oscar.core.loading import get_class


class CheckoutConfig(apps.CheckoutConfig):
	name = 'dehy.appz.checkout'
	label = 'checkout'
	verbose_name = _('Checkout')
	namespace = 'checkout'

	def ready(self):
		self.checkout_view = get_class('checkout.views', 'CheckoutIndexView')
		self.user_info_view = get_class('checkout.views', 'CheckoutIndexView')
		self.shipping_view = get_class('checkout.views', 'ShippingView')
		self.additional_info_view = get_class('checkout.views', 'AdditionalInfoView')
		self.billing_view = get_class('checkout.views', 'BillingView')
		self.thankyou_view = get_class('checkout.views', 'ThankYouView')

	def get_urls(self):
		urls = [
			path('', self.checkout_view.as_view(), name='checkout'),
			path('', self.checkout_view.as_view(), name='index'),
			path('user_info/', self.user_info_view.as_view(), name='user_info'),
			path('shipping/', self.shipping_view.as_view(), name='shipping'),
			path('additional_info/', self.additional_info_view.as_view(), name='additional_info'),
			path('billing/', self.billing_view.as_view(), name='billing'),
			path('place_order/', self.billing_view.as_view(preview=True), name='place_order'),
			path('thank_you/', self.thankyou_view.as_view(), name='thank_you'),
			path('thank-you/', self.thankyou_view.as_view(), name='thank_you'),
		]
		return self.post_process_urls(urls)
