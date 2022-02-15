from oscar.apps.checkout import views
from oscar.apps.payment import models
from oscar.core.loading import get_class, get_classes, get_model
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .facade import Facade
from django.conf import settings
from django.utils.decorators import method_decorator

from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN
StripeTokenForm, ShippingAddressForm, ShippingMethodForm, GatewayForm \
	= get_classes('checkout.forms', ['StripeTokenForm', 'ShippingAddressForm', 'ShippingMethodForm', 'GatewayForm'])

BankcardForm, BillingAddressForm \
	= get_classes('payment.forms', ['BankcardForm', 'BillingAddressForm'])


SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')

class IndexView(views.IndexView):
	"""
	First page of the checkout.  We prompt user to either sign in, or
	to proceed as a guest (where we still collect their email address).
	"""
	template_name = 'dehy/checkout/gateway.html'
	form_class = GatewayForm
	success_url = reverse_lazy('checkout:shipping-address')
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid']


class PaymentDetailsView(views.PaymentDetailsView):
	"""
	For taking the details of payment and creating the order.
	This view class is used by two separate URLs: 'payment-details' and
	'preview'. The `preview` class attribute is used to distinguish which is
	being used. Chronologically, `payment-details` (preview=False) comes before
	`preview` (preview=True).
	If sensitive details are required (e.g. a bankcard), then the payment details
	view should submit to the preview URL and a custom implementation of
	`validate_payment_submission` should be provided.
	- If the form data is valid, then the preview template can be rendered with
	  the payment-details forms re-rendered within a hidden div so they can be
	  re-submitted when the 'place order' button is clicked. This avoids having
	  to write sensitive data to disk anywhere during the process. This can be
	  done by calling `render_preview`, passing in the extra template context
	  vars.
	- If the form data is invalid, then the payment details templates needs to
	  be re-rendered with the relevant error messages. This can be done by
	  calling `render_payment_details`, passing in the form instances to pass
	  to the templates.
	The class is deliberately split into fine-grained methods, responsible for
	only one thing.  This is to make it easier to subclass and override just
	one component of functionality.
	All projects will need to subclass and customise this class as no payment
	is taken by default.
	"""
	template_name = 'dehy/checkout/payment_details.html'
	template_name_preview = 'dehy/checkout/preview.html'

	# These conditions are extended at runtime depending on whether we are in
	# 'preview' mode or not.
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured',
		'check_shipping_data_is_captured']

	# If preview=True, then we render a preview template that shows all order
	# details ready for submission.
	preview = False

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, *args, **kwargs):

		context_data = super().get_context_data(*args, **kwargs)
		context_data['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
		context_data['billing_address_form'] = kwargs.get('billing_address_form', BillingAddressForm())
		shipping_addr = context_data.get('shipping_address', None)
		if shipping_addr:
			# print(f'\n shipping_addr: {dir(shipping_addr)}')

			context_data['billing_address_form'].initial = {
				'first_name':shipping_addr.first_name, 'last_name':shipping_addr.last_name,
				'line1': shipping_addr.line1, 'line2': shipping_addr.line2, 'city':shipping_addr.city,
				'state':shipping_addr.state, 'postcode':shipping_addr.postcode,
				'country':shipping_addr.country, 'phone_number':shipping_addr.phone_number
			}

		if self.preview:
			context_data['stripe_token_form'] = StripeTokenForm(self.request.POST)
			context_data['order_total_incl_tax_cents'] = (context_data['order_total'].incl_tax * 100).to_integral_value()
		else:
			context_data['order_total_incl_tax_cents'] = (context_data['order_total'].incl_tax * 100).to_integral_value()
			context_data['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY

		print(context_data)

		return context_data

	def handle_payment(self, order_number, total, *args, **kwargs):
		print('\n** handling payment **\n')
		print(f'\n dir self {dir(self)}')
		print(f'\n dir request {dir(self.request)}')
		print(f'\n self.args {self.args}')
		print(f'\n self.kwargs {self.kwargs}')

		print(f'\n dir checkout_session {dir(self.checkout_session)}')
		print(f'\n shipping address set: {self.checkout_session.is_shipping_address_set()}')
		print(f'\n is_billing_address_same_as_shipping: {self.checkout_session.is_billing_address_same_as_shipping()}')
		print(f'\n is_billing_address_set: {self.checkout_session.is_billing_address_set()}')
		print(f'\n payment_method: {self.checkout_session.payment_method()}')

		print(f'\n dir kwargs {[x for x in kwargs.items()]}')


		basket = self.request.basket

		shipping_address_obj = self.get_shipping_address(self.request.basket)
		print('\n dir shipping_address: ', dir(shipping_address_obj))

		shipping = {
			'address': {
				'city': shipping_address_obj.city,
				'country': shipping_address_obj.country,
				'line1': shipping_address_obj.line1,
				'line2': shipping_address_obj.line2,
				'postal_code': shipping_address_obj.postcode,
				'state': shipping_address_obj.state,
			},
			'name': shipping_address_obj.name,
		}

		print(f'\n kwargs shipping_address {kwargs["shipping_address"]}')


		stripe_ref = Facade().charge(
			order_number,
			total,
			card=self.request.POST[STRIPE_TOKEN],
			description=self.payment_description(order_number, total, **kwargs),
			metadata=self.payment_metadata(order_number, total, **kwargs))

		source_type, __ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)
		source = Source(
			source_type=source_type,
			currency=settings.STRIPE_CURRENCY,
			amount_allocated=total.incl_tax,
			amount_debited=total.incl_tax,
			reference=stripe_ref)
		self.add_payment_source(source)

		self.add_payment_event(PAYMENT_EVENT_PURCHASE, total.incl_tax)

	def payment_description(self, order_number, total, **kwargs):
		return self.request.POST[STRIPE_EMAIL]

	def payment_metadata(self, order_number, total, **kwargs):
		return {'order_number': order_number}

	#### OLD ####
	# def handle_payment(self, order_number, total, **kwargs):
	# 	# method = self.checkout_session.payment_method()
	# 	# Talk to payment gateway.  If unsuccessful/error, raise a
	# 	# PaymentError exception which we allow to percolate up to be caught
	# 	# and handled by the core PaymentDetailsView.
	#
	# 	gateway = ''
	# 	reference = gateway.pre_auth(order_number, total.incl_tax, kwargs['bankcard'])
	#
	# 	# Payment successful! Record payment source
	# 	source_type, __ = models.SourceType.objects.get_or_create(
	# 		name="SomeGateway")
	# 	source = models.Source(
	# 		source_type=source_type,
	# 		amount_allocated=total.incl_tax,
	# 		reference=reference)
	# 	self.add_payment_source(source)
	#
	# 	# Record payment event
	# 	self.add_payment_event('pre-auth', total.incl_tax)
	#

class PaymentMethodView(views.PaymentMethodView):
	"""
	View for a user to choose which payment method(s) they want to use.
	This would include setting allocations if payment is to be split
	between multiple sources. It's not the place for entering sensitive details
	like bankcard numbers though - that belongs on the payment details view.
	"""
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured',
		'check_shipping_data_is_captured']
	skip_conditions = ['skip_unless_payment_is_required']
	success_url = reverse_lazy('checkout:payment-details')

	def get(self, request, *args, **kwargs):
		# By default we redirect straight onto the payment details view. Shops
		# that require a choice of payment method may want to override this
		# method to implement their specific logic.
		return self.get_success_response()

	def get_success_response(self):
		return redirect(self.get_success_url())

	def get_success_url(self):
		return str(self.success_url)