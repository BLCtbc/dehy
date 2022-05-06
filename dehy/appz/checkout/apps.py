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
		self.checkout_basket_view = get_class('checkout.views', 'ShippingView')
		self.shipping_view = get_class('checkout.views', 'ShippingView')
		# self.shipping_address_view = get_class('checkout.views', 'ShippingAddressRedirectView')
		# self.shipping_method_view = get_class('checkout.views', 'ShippingMethodRedirectView')

		self.additional_info_view = get_class('checkout.views', 'AdditionalInfoView')
		self.billing_view = get_class('checkout.views', 'BillingView')
		self.place_order_view = get_class('checkout.views', 'PlaceOrderView')
		self.thankyou_view = get_class('checkout.views', 'ThankYouView')


	def get_urls(self):
		urls = [
			path('', self.checkout_view.as_view(), name='checkout'),
			path('', self.checkout_view.as_view(), name='index'),
			path('basket/', self.checkout_basket_view.as_view(), name='basket'),
			path('user_info/', self.user_info_view.as_view(), name='user_info'),
			path('shipping/', self.shipping_view.as_view(), name='shipping'),
			path('additional_info/', self.additional_info_view.as_view(), name='additional_info'),
			path('billing/', self.billing_view.as_view(), name='billing'),
			path('place_order/', self.place_order_view.as_view(preview=True), name='place_order'),
			# path('shipping-address/', self.shipping_address_view.as_view(), name='shipping-address'),
			# path('shipping-method/', self.shipping_method_view.as_view(), name='shipping-method'),

			# path('preview/', self.place_order_view.as_view(preview=True), name='preview'),

			path('thank_you/', self.thankyou_view.as_view(), name='thank_you'),
			path('thank-you/', self.thankyou_view.as_view(), name='thank_you'),
		]
		return self.post_process_urls(urls)
