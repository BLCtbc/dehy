from oscar.apps.checkout import views
from oscar.apps.payment import models
from oscar.core.loading import get_class, get_classes, get_model
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

ShippingAddressForm, ShippingMethodForm, GatewayForm \
	= get_classes('checkout.forms', ['ShippingAddressForm', 'ShippingMethodForm', 'GatewayForm'])

BankcardForm, BillingAddressForm \
	= get_classes('payment.forms', ['BankcardForm', 'BillingAddressForm'])

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

	def get_context_data(self, *args, **kwargs):

		context_data = super().get_context_data(*args, **kwargs)
		context_data['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
		context_data['billing_address_form'] = kwargs.get('billing_address_form', BillingAddressForm())
		shipping_addr = context_data.get('shipping_address', None)
		if shipping_addr:
			print(dir(shipping_addr))
			print(f'\n active address fields: {shipping_addr.active_address_fields()}')

			context_data['billing_address_form'].initial = {
				'first_name':shipping_addr.first_name, 'last_name':shipping_addr.last_name,
				'line1': shipping_addr.line1, 'line2': shipping_addr.line2, 'city':shipping_addr.city,
				'state':shipping_addr.state, 'postcode':shipping_addr.postcode,
				'country':shipping_addr.country, 'phone_number':shipping_addr.phone_number
			}

		print(context_data)

		return context_data

	def handle_payment(self, order_number, total, **kwargs):
		print('\n *** handling payment *** \n')
		# method = self.checkout_session.payment_method()
		# Talk to payment gateway.  If unsuccessful/error, raise a
		# PaymentError exception which we allow to percolate up to be caught
		# and handled by the core PaymentDetailsView.

		gateway = ''
		reference = gateway.pre_auth(order_number, total.incl_tax, kwargs['bankcard'])

		# Payment successful! Record payment source
		source_type, __ = models.SourceType.objects.get_or_create(
			name="SomeGateway")
		source = models.Source(
			source_type=source_type,
			amount_allocated=total.incl_tax,
			reference=reference)
		self.add_payment_source(source)

		# Record payment event
		self.add_payment_event('pre-auth', total.incl_tax)


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