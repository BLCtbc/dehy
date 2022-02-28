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
		self.shipping_view = get_class('checkout.views', 'ShippingView')
		self.additional_info_view = get_class('checkout.views', 'AdditionalInfoView')
		self.billing_view = get_class('checkout.views', 'BillingView')

		# self.additional_info_view = get_class('checkout.views', 'AdditionalInfoView')
		# self.billing_view = get_class('checkout.views', 'BillingView')

		# self.index_view = get_class('checkout.views', 'IndexView')
		# self.shipping_address_view = get_class('checkout.views', 'ShippingAddressView')
		# self.user_address_update_view = get_class('checkout.views',
		#                                           'UserAddressUpdateView')
		# self.user_address_delete_view = get_class('checkout.views',
		#                                           'UserAddressDeleteView')
		# self.shipping_method_view = get_class('checkout.views', 'ShippingMethodView')
		# self.payment_method_view = get_class('checkout.views', 'PaymentMethodView')
		# self.payment_details_view = get_class('checkout.views', 'PaymentDetailsView')
		# self.thankyou_view = get_class('checkout.views', 'ThankYouView')

	def get_urls(self):
		urls = [
			path('', self.checkout_view.as_view(), name='checkout'),
			path('shipping/', self.shipping_view.as_view(), name='shipping'),
			path('additional_info/', self.additional_info_view.as_view(), name='additional_info'),
			path('billing/', self.billing_view.as_view(), name='billing'),

			# path('additional_info/', self.additional_info_view.as_view(), name='additional_info'),
			# path('billing/', self.billing_view.as_view(), name='additional_info'),

			# path('', self.index_view.as_view(), name='index'),
			#
			# # Shipping/user address views
			# path('shipping-address/', self.shipping_address_view.as_view(), name='shipping-address'),
			# path('user-address/edit/<int:pk>/', self.user_address_update_view.as_view(), name='user-address-update'),
			# path('user-address/delete/<int:pk>/', self.user_address_delete_view.as_view(), name='user-address-delete'),
			#
			# # Shipping method views
			# path('shipping-method/', self.shipping_method_view.as_view(), name='shipping-method'),
			#
			# # Payment views
			# path('payment-method/', self.payment_method_view.as_view(), name='payment-method'),
			# path('payment-details/', self.payment_details_view.as_view(), name='payment-details'),
			#
			# # Preview and thankyou
			# path('preview/', self.payment_details_view.as_view(preview=True), name='preview'),
			# path('thank-you/', self.thankyou_view.as_view(), name='thank-you'),
		]
		return self.post_process_urls(urls)

	# def get_url_decorator(self, pattern):
	#     if not settings.OSCAR_ALLOW_ANON_CHECKOUT:
	#         return login_required
	#     if pattern.name.startswith('user-address'):
	#         return login_required
	#     return None