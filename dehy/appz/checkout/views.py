from oscar.apps.checkout import views
from oscar.apps.payment import models
from oscar.core.loading import get_class, get_classes, get_model
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.generic import TemplateView
from .facade import Facade

# from oscar.apps.basket.middleware import BasketMiddleware

import json

from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN


Repository = get_class('shipping.repository', 'Repository')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')

def get_shipping(request):
	pass

def get_billing(request):
	pass

class CheckoutView(TemplateView, CheckoutSessionMixin):
	StripeTokenForm, ShippingAddressForm, ShippingMethodForm, UserInfoForm, ShippingForm \
		= get_classes('checkout.forms', ['StripeTokenForm', 'ShippingAddressForm', 'ShippingMethodForm', 'UserInfoForm', 'ShippingForm'])

	BankcardForm, BillingAddressForm \
		= get_classes('payment.forms', ['BankcardForm', 'BillingAddressForm'])

	CHECKOUT_FORMS = {
		'USER_INFO': {'forms': [UserInfoForm]},
		'SHIPPING': {'forms': [ShippingAddressForm, ShippingMethodForm]},
		'ADDITIONAL_INFO': '',
		'BILLING':[BillingAddressForm, BankcardForm],
		'PREVIEW_AND_CONFIRM': '',
	}
	CHECKOUT_FLOW = list(CHECKOUT_FORMS.keys())

	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid'
	]

	template_name = "dehy/checkout/checkout_v2.html"
	form_class = UserInfoForm

	def get_context_data(self, *args, **kwargs):
		print('get_context_data')
		context_data = super().get_context_data(*args, **kwargs)
		print(f'\n context_data: {context_data}')

		return context_data


	def validate_user_info(self, request):
		valid = False
		self.pre_conditions += ['check_user_email_is_captured']
		self.check_pre_conditions(request)
		form = self.UserInfoForm(request.POST)

		if form.is_valid():
			valid = True

		return valid

	def post(self, request, *args, **kwargs):
		print('\n *** post() ***')
		data = {}
		if request.is_ajax():
			# get the form
			# checkout_step = request.POST.get('checkout_step', None).upper()
			print(f'\n request.POST: {request.POST}')
			print(f'\n dir(request): {dir(request)}')

			if request.resolver_match.url_name is 'shipping':

				if self.validate_user_info(request):
					print('\n **** validated user_info **** \n')
					data['forms'] = [self.ShippingAddressForm(), self.ShippingMethodForm()]
					data['next_section'] = 'shipping'

				## also need to do any other user validation that oscar might do


			elif request.resolver_match.url_name is 'additional_info':
				# validate shipping forms
				# do oscar stuff, like check_pre_conditions
				self.pre_conditions += ['check_shipping_data_is_captured']
				self.check_pre_conditions(request)
				if all([self.ShippingAddressForm(request.POST).is_valid(), self.ShippingMethodForm(request.POST).is_valid()]):
					data['next_section'] = 'additional_info'
					pass

			elif request.resolver_match.url_name is 'billing':
				pass

			# check if all forms are valid
			# if all(list(map(lambda x: x(request.POST.get('form')).is_valid(), forms))):
			# 	print('all passing')
				# if so, do stuff with the form data, depending on which form it was
				# and
				# get the next form
				# then return it
			print('data: ', data)
			response = JsonResponse(data)

		return response

	def get(self, request, *args, **kwargs):
		print('\n*** get() ***')
		response = super().get(request, *args, **kwargs)
		response.context_data.update({'form': self.form_class()})
		return response


	def get_available_shipping_methods(self):
		"""
		Returns all applicable shipping method objects for a given basket.
		"""
		# Shipping methods can depend on the user, the contents of the basket
		# and the shipping address (so we pass all these things to the
		# repository).  I haven't come across a scenario that doesn't fit this
		# system.
		return Repository().get_shipping_methods(
			basket=self.request.basket, user=self.request.user,
			shipping_addr=self.get_shipping_address(self.request.basket),
			request=self.request)



	def get_next_form(self, request, current_step):
		current_step = CHECKOUT_FLOW.index(current_step)
		return CHECKOUT_FORMS[CHECKOUT_FLOW[CHECKOUT_FLOW.index(current_step)+1]]

# class IndexView(views.IndexView):
# 	"""
# 	First page of the checkout.  We prompt user to either sign in, or
# 	to proceed as a guest (where we still collect their email address).
# 	"""
# 	template_name = 'dehy/checkout/gateway.html'
# 	form_class = UserInfoForm
# 	success_url = reverse_lazy('checkout:shipping-address')
# 	pre_conditions = [
# 		'check_basket_is_not_empty',
# 		'check_basket_is_valid']

	# def get_context_data(self, *args, **kwargs):
	#
	# 	context_data = super().get_context_data(*args, **kwargs)
	# 	print(f'\n context_data: {context_data}')
	#
	# 	shipping = context_data.get('shipping_address', None)
	# 	context_data['stripe_data'] = {
	# 		'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
	# 	}
	# 	payment_intent = Facade().payment_intent(total=context_data['order_total'], shipping=shipping) or None
	# 	print(f'\n payment_intent: {payment_intent}')
		# if payment_intent:
			# print(f'\n payment intent: {payment_intent}')
			# self.request.basket.payment_intent_id = payment_intent.id
			# context_data['stripe_data']['client_secret'] = payment_intent.client_secret
			# self.checkout_session.client_secret = payment_intent.client_secret
			# self.checkout_session.payment_intent_id = payment_intent.id

		# context_data['stripe_data']['client_secret'] = Facade().payment_intent(total=context_data['order_total'], shipping=shipping).client_secret

		# context_data['stripe_client_secret'] = self.get_payment_intent(total=context_data['order_total'], shipping=shipping).client_secret

		# return context_data


# class ShippingAddressView(views.ShippingAddressView):
# 	template_name = 'dehy/checkout/shipping_address.html'

# class UserAddressUpdateView(views.UserAddressUpdateView):
# 	template_name = 'dehy/checkout/user_address_form.html'
#
# class UserAddressDeleteView(views.UserAddressDeleteView):
# 	template_name = 'dehy/checkout/user_address_delete.html'

# class ShippingMethodView(views.ShippingMethodView):
# 	template_name = 'dehy/checkout/shipping_methods.html'

# class PaymentDetailsView(views.PaymentDetailsView):
# 	"""
# 	For taking the details of payment and creating the order.
# 	This view class is used by two separate URLs: 'payment-details' and
# 	'preview'. The `preview` class attribute is used to distinguish which is
# 	being used. Chronologically, `payment-details` (preview=False) comes before
# 	`preview` (preview=True).
# 	If sensitive details are required (e.g. a bankcard), then the payment details
# 	view should submit to the preview URL and a custom implementation of
# 	`validate_payment_submission` should be provided.
# 	- If the form data is valid, then the preview template can be rendered with
# 	  the payment-details forms re-rendered within a hidden div so they can be
# 	  re-submitted when the 'place order' button is clicked. This avoids having
# 	  to write sensitive data to disk anywhere during the process. This can be
# 	  done by calling `render_preview`, passing in the extra template context
# 	  vars.
# 	- If the form data is invalid, then the payment details templates needs to
# 	  be re-rendered with the relevant error messages. This can be done by
# 	  calling `render_payment_details`, passing in the form instances to pass
# 	  to the templates.
# 	The class is deliberately split into fine-grained methods, responsible for
# 	only one thing.  This is to make it easier to subclass and override just
# 	one component of functionality.
# 	All projects will need to subclass and customise this class as no payment
# 	is taken by default.
# 	"""
# 	template_name = 'dehy/checkout/payment_details.html'
# 	template_name_preview = 'dehy/checkout/preview.html'
#
# 	# These conditions are extended at runtime depending on whether we are in
# 	# 'preview' mode or not.
# 	pre_conditions = [
# 		'check_basket_is_not_empty',
# 		'check_basket_is_valid',
# 		'check_user_email_is_captured',
# 		'check_shipping_data_is_captured']
#
# 	# If preview=True, then we render a preview template that shows all order
# 	# details ready for submission.
# 	preview = False
#
# 	@method_decorator(csrf_exempt)
# 	def dispatch(self, request, *args, **kwargs):
# 		return super().dispatch(request, *args, **kwargs)
#
# 	def get_context_data(self, *args, **kwargs):
#
# 		context_data = super().get_context_data(*args, **kwargs)
#
# 		## for testing
# 		context_data['old'] = True
#
# 		context_data['bankcard_form'] = kwargs.get('bankcard_form', BankcardForm())
# 		context_data['billing_address_form'] = kwargs.get('billing_address_form', BillingAddressForm())
# 		shipping = context_data.get('shipping_address', None)
# 		if shipping:
#
# 			context_data['billing_address_form'].initial = {
# 				'first_name':shipping.first_name, 'last_name':shipping.last_name,
# 				'line1': shipping.line1, 'line2': shipping.line2, 'city':shipping.city,
# 				'state':shipping.state, 'postcode':shipping.postcode,
# 				'country':shipping.country, 'phone_number':shipping.phone_number
# 			}
#
# 		context_data['stripe_data'] = {}
#
# 		payment_intent = Facade().payment_intent(total=context_data['order_total'], shipping=shipping)
# 		context_data['stripe_data']['client_secret'] = payment_intent.client_secret
# 		context_data['stripe_data']['publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
#
# 		if self.preview:
# 			context_data['stripe_token_form'] = StripeTokenForm(self.request.POST)
# 			context_data['order_total_incl_tax_cents'] = (context_data['order_total'].incl_tax * 100).to_integral_value()
# 		else:
# 			context_data['order_total_incl_tax_cents'] = (context_data['order_total'].incl_tax * 100).to_integral_value()
#
# 		# payment_intent = Facade().payment_intent(total=context_data['order_total'], shipping=shipping)
# 		context_data['stripe_data']['client_secret'] = payment_intent.client_secret
# 		context_data['stripe_data']['publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
#
# 		return context_data
#
# 	# def get_payment_intent(self, total, shipping, *args, **kwargs):
# 	# 	stripe_payment_intent = Facade().create_payment_intent(total, shipping=shipping)
# 	# 	return stripe_payment_intent
#
#
# 	def handle_payment(self, order_number, total, *args, **kwargs):
#
# 		print(f'\n dir(self): {dir(self)}')
# 		basket = self.request.basket
# 		shipping_address_obj = self.get_shipping_address(self.request.basket)
#
# 		shipping = {
# 			'address': {
# 				'city': shipping_address_obj.city,
# 				'country': shipping_address_obj.country,
# 				'line1': shipping_address_obj.line1,
# 				'line2': shipping_address_obj.line2,
# 				'postal_code': shipping_address_obj.postcode,
# 				'state': shipping_address_obj.state,
# 			},
# 			'name': shipping_address_obj.name,
# 			'phone': shipping_address_obj.phone_number
# 		}
#
# 		# print('self: ', self.request.GET.get(billing_address_form))
# 		billing_addr_form = self.request.GET.get('billing_address_form', None)
#
# 		if hasattr(billing_addr_form, 'same_as_shipping'):
# 			self.checkout_session.bill_to_shipping_address()
#
# 		else:
# 			## need to set the billing address elsewhere
# 			## self.get_billing_address()
# 			pass
#
#
# 		stripe_ref = Facade().confirm_payment_intent(
# 			id=self.request.basket.payment_intent_id,
# 			card=self.request.POST[STRIPE_TOKEN],
# 			shipping=shipping, order_number=order_number,
# 			description=self.payment_description(order_number, total, **kwargs),
# 			metadata=self.payment_metadata(order_number, total, **kwargs)
# 		)
#
# 		# stripe_ref = Facade().charge(
# 		# 	order_number,
# 		# 	total,
# 		# 	shipping=shipping,
# 		# 	card=self.request.POST[STRIPE_TOKEN],
# 		# 	description=self.payment_description(order_number, total, **kwargs),
# 		# 	metadata=self.payment_metadata(order_number, total, **kwargs))
#
#
#
# 		source_type, __ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)
# 		source = Source(
# 			source_type=source_type,
# 			currency=settings.STRIPE_CURRENCY,
# 			amount_allocated=total.incl_tax,
# 			amount_debited=total.incl_tax,
# 			reference=stripe_ref)
#
# 		self.add_payment_source(source)
#
# 		self.add_payment_event(PAYMENT_EVENT_PURCHASE, total.incl_tax)
#
# 	def payment_description(self, order_number, total, **kwargs):
# 		return self.request.POST[STRIPE_EMAIL]
#
# 	def payment_metadata(self, order_number, total, **kwargs):
# 		return {'order_number': order_number}

#
# class PaymentMethodView(views.PaymentMethodView):
# 	"""
# 	View for a user to choose which payment method(s) they want to use.
# 	This would include setting allocations if payment is to be split
# 	between multiple sources. It's not the place for entering sensitive details
# 	like bankcard numbers though - that belongs on the payment details view.
# 	"""
# 	pre_conditions = [
# 		'check_basket_is_not_empty',
# 		'check_basket_is_valid',
# 		'check_user_email_is_captured',
# 		'check_shipping_data_is_captured']
# 	skip_conditions = ['skip_unless_payment_is_required']
# 	success_url = reverse_lazy('checkout:payment-details')
#
# 	def get(self, request, *args, **kwargs):
# 		# By default we redirect straight onto the payment details view. Shops
# 		# that require a choice of payment method may want to override this
# 		# method to implement their specific logic.
# 		return self.get_success_response()
#
# 	def get_success_response(self):
# 		return redirect(self.get_success_url())
#
# 	def get_success_url(self):
# 		return str(self.success_url)
