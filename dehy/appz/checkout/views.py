from oscar.apps.checkout import signals, views
from oscar.apps.payment import models
from oscar.core.loading import get_class, get_classes, get_model
from oscar.apps.checkout import exceptions
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib import messages
from django.http import QueryDict, JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from decimal import Decimal as D
TWOPLACES = D(10)**-2

from .facade import Facade

from urllib.parse import quote
import json, logging, requests, sys, xmltodict

from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN

BasketView = get_class('basket.views', 'BasketView')
basket_model = get_model('basket', 'Basket')

BillingAddressForm, StripeTokenForm, ShippingAddressForm, ShippingMethodForm, UserInfoForm, AdditionalInfoForm, SubmitOrderForm, CountryAndPostcodeForm \
	= get_classes('checkout.forms', ['BillingAddressForm', 'StripeTokenForm', 'ShippingAddressForm', 'ShippingMethodForm', 'UserInfoForm', 'AdditionalInfoForm', 'PurchaseConfirmationForm', 'FakeShippingAddressForm'])

RedirectRequired, UnableToTakePayment, PaymentError = get_classes('payment.exceptions', ['RedirectRequired','UnableToTakePayment','PaymentError'])

Repository = get_class('shipping.repository', 'Repository')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')
OrderDispatcher = get_class('order.utils', 'OrderDispatcher')
AdditionalInfoQuestionnaire = get_class('dehy.appz.generic.models', 'AdditionalInfoQuestionnaire')
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')

SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
Country = get_model('address', 'Country')
ShippingAddress = get_model('order', 'ShippingAddress')

logger = logging.getLogger('oscar.checkout')

def Deb(msg=''):
	print(f"Debug {sys._getframe().f_back.f_lineno}: {msg}")

def get_city_and_state(postcode=None):
	data = {}
	BASE_URL = 'https://secure.shippingapis.com/ShippingAPI.dll?API=CityStateLookup'

	if not postcode:
		data['error'] = 'Bad Request'

	else:
		xml = f'<CityStateLookupRequest USERID="{settings.USPS_USERNAME}"><ZipCode ID= "0"><Zip5>{postcode}</Zip5></ZipCode></CityStateLookupRequest>'
		url = f"{BASE_URL}&XML={xml}"
		xml_response = requests.get(url).content
		usps_response = json.loads(json.dumps(xmltodict.parse(xml_response)))['CityStateLookupResponse']
		if 'Error' in usps_response['ZipCode'].keys():
			data['error'] = usps_response['ZipCode']['Error']

		else:
			data['city'] = usps_response['ZipCode']['City']
			data['line4'] = usps_response['ZipCode']['City']
			data['state'] = usps_response['ZipCode']['State']

	return data

def ajax_set_shipping_method(request):
	data = {}
	status_code = 400

	checkout_session = CheckoutSessionData(request)
	print('dir(request.basket): ', dir(request.basket))
	print(f'dir(checkout_session): {dir(checkout_session)}')
	method_code = request.POST.get('method_code', None)
	shipping_methods = checkout_session.get_stored_shipping_methods()

	method_codes = [method.code for method in shipping_methods]
	if method_code and method_code in method_codes:
		selected_method = list(filter(lambda x: getattr(x, 'code', None)==method_code, shipping_methods))[0]
		status_code = 200
		checkout_session.use_shipping_method(method_code)

		order = Facade().update_or_create_order(request.basket, shipping_cost={'cost':selected_method.calculate(request.basket).excl_tax, 'code':selected_method.code, 'name':selected_method.name})
		checkout_session.set_order_number(order.id)
		data['subtotal'] = str(D(order.amount_subtotal/100).quantize(TWOPLACES))
		data['total_tax'] = str(D(order.total_details.amount_tax/100).quantize(TWOPLACES))
		data['shipping_charge'] = str(D(order.total_details.amount_shipping/100).quantize(TWOPLACES))
		data['order_total'] = str(D(order.amount_total/100).quantize(TWOPLACES))


	response = JsonResponse(data)
	response.status_code = status_code
	return response


def get_shipping_methods(request, shipping_addr, frontend_formatted=False, return_status_code=False):

	shipping_methods = []
	if type(shipping_addr) is str:
		shipping_addr = json.loads(shipping_addr)

	shipping_address_form = CountryAndPostcodeForm(shipping_addr)
	methods = []
	if shipping_address_form.is_valid():

		address_fields = dict((k, v) for (k, v) in shipping_address_form.instance.__dict__.items() if not k.startswith('_'))
		country_obj = Country.objects.get(iso_3166_1_a2=address_fields.get('country_id'))
		shipping_address = ShippingAddress(**address_fields)

		methods,status_code = Repository().get_shipping_methods(
					basket=request.basket, user=request.user,
					shipping_addr=shipping_address, request=request)

		checkout_session = CheckoutSessionData(request)
		checkout_session.store_shipping_methods(request.basket, methods)

		for method in methods:
			cost = method.calculate(request.basket).excl_tax
			shipping_methods.append({'name': method.name, 'cost':cost, 'code':method.code})

		shipping_methods = sorted(shipping_methods, key=lambda x: x['cost'])

		methods = shipping_methods if frontend_formatted else methods
		methods = [methods, status_code] if return_status_code else methods

	return methods

# also 'corrects' city and state based on postcode
def ajax_get_shipping_methods(request):

	print('\n request.POST: ', request.POST)
	data = {}
	post_data = request.POST.copy()
	status_code = 400

	if post_data.get('postcode', None):
		city_and_state_data = get_city_and_state(request.POST.get('postcode'))
		post_data.update(city_and_state_data)
		data.update(city_and_state_data)

	checkout_session = CheckoutSessionData(request)
	shipping_address_form = CountryAndPostcodeForm(post_data)

	if not shipping_address_form.is_valid():
		print(f'\n form.errors: {shipping_address_form.errors}')

	else:
		status_code = 200
		address_fields = dict((k, v) for (k, v) in shipping_address_form.instance.__dict__.items() if not k.startswith('_'))
		country_obj = Country.objects.get(iso_3166_1_a2=address_fields.get('country_id'))

		shipping_address = ShippingAddress(**address_fields)
		checkout_session.ship_to_new_address(address_fields)
		methods, status_code = get_shipping_methods(request, post_data, True, True)
		data['shipping_methods'] = []

		if methods:

			data['shipping_methods'] = methods
			data['shipping_postcode'] = address_fields['postcode']
			checkout_session = CheckoutSessionData(request)

			data['shipping_charge'] = data['shipping_methods'][0]['cost']
			checkout_session.use_shipping_method(data['shipping_methods'][0]['code'])


			order = Facade().update_or_create_order(request.basket, shipping_details=address_fields, shipping_cost={'cost':data['shipping_charge'], 'code':data['shipping_methods'][0]['code']})
			checkout_session.set_order_number(order.id)
			data['order_total'] = str(D(order.amount_total/100).quantize(TWOPLACES))
			data['subtotal'] = str(D(order.amount_subtotal/100).quantize(TWOPLACES))
			data['total_tax'] = str(D(order.total_details.amount_tax/100).quantize(TWOPLACES))


	response = JsonResponse(data)
	response.status_code = status_code
	return response

def update_tax_amount(request):

	pass

class CheckoutIndexView(CheckoutSessionMixin, generic.FormView):

	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid'
	]
	success_url = reverse_lazy('checkout:shipping')
	template_name = "dehy/checkout/checkout_v2.html"
	form_class = UserInfoForm

	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)
		return context_data

	def form_valid(self, form):
		# the stripe customer object should be created along the same time as a user account is setup
		if form.is_guest_checkout() or form.is_new_account_checkout():
			email = form.cleaned_data['username']
			self.checkout_session.set_guest_email(email)
			# We raise a signal to indicate that the user has entered the
			# checkout process by specifying an email address.
			signals.start_checkout.send_robust(
				sender=self, request=self.request, email=email)

			if form.is_new_account_checkout():
				messages.info(
					self.request,
					_("Create your account and then you will be redirected "
					  "back to the checkout process"))
				self.success_url = "%s?next=%s&email=%s" % (
					reverse('customer:register'),
					reverse('checkout:shipping'),
					quote(email)
				)
		else:
			user = form.get_user()
			login(self.request, user)

			# We raise a signal to indicate that the user has entered the
			# checkout process.
			signals.start_checkout.send_robust(
				sender=self, request=self.request)

		return redirect(self.get_success_url())

	def get_form_structure(self, form, use_labels=True):
		return super().get_form_structure(form, use_labels=True)

	def post(self, request, *args, **kwargs):
		data = {}
		status_code = 400
		form = self.form_class(request, request.POST)
		response = super().post(request, *args, **kwargs)

		if request.is_ajax() and form.is_valid():

			status_code = 200
			data['section'] = 'user_info'
			# send all elems to be previewed, along with the values
			data['preview_elems'] = {'email': form.cleaned_data['username']}
			self.get_form_structure(ShippingAddressForm, use_labels=True)
			## get or create the stripe customer object
			response = JsonResponse(data)


		response.status_code = status_code
		return response

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		email = self.checkout_session.get_guest_email()
		if email:
			kwargs['initial'] = {
				'username': email,
			}
		return kwargs

	def get(self, request, *args, **kwargs):

		response = super().get(request, *args, **kwargs)
		basket_view = BasketView.as_view()(request)

		if request.basket.stripe_order_id:
			order = Facade().update_order(request.basket)
		else:
			order = Facade().create_order(request.basket)

		response.context_data.update({
			'form': self.form_class(),
			'basket_summary_context_data': basket_view.context_data,
			'is_shipping_address_set': self.checkout_session.is_shipping_address_set(),
			'is_shipping_method_set':self.checkout_session.is_shipping_method_set(request.basket)
		})
		return response


class ShippingView(CheckoutSessionMixin, generic.FormView):
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured'
	]
	success_url = reverse_lazy('checkout:additional_info')
	template_name = "dehy/checkout/checkout_v2.html"
	form_class = ShippingAddressForm

	# def get_shipping_method(self, basket, shipping_address=None, **kwargs):
	# 	"""
	# 	Return the selected shipping method instance from this checkout session
	# 	The shipping address is passed as we need to check that the method
	# 	stored in the session is still valid for the shipping address.
	# 	"""
	#
	# 	code = self.checkout_session.shipping_method_code(basket)
	#
	# 	methods = Repository().get_shipping_methods(
	# 		basket=basket, user=self.request.user,
	# 		shipping_addr=shipping_address, request=self.request)
	#
	# 	for method in methods:
	# 		if method.code == code:
	# 			return method

	def get_available_addresses(self):
		# Include only addresses where the country is flagged as valid for
		# shipping. Also, use ordering to ensure the default address comes
		# first.
		return self.request.user.addresses.filter(
			country__is_shipping_country=True).order_by(
			'-is_default_for_shipping')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['methods'] = self._methods
		if self.request.user.is_authenticated:
			# Look up address book data
			ctx['addresses'] = self.get_available_addresses()

		print(f'\n *** context_data: {ctx}')
		return ctx


	## must be called prior to get_context_data(), which is also called by super().get()
	def get_available_shipping_methods(self):
		"""
		Returns all applicable shipping method objects for a given basket.
		"""
		methods, status_code = Repository().get_shipping_methods(
			basket=self.request.basket, user=self.request.user,
			shipping_addr=self.get_shipping_address(self.request.basket),
			request=self.request)

		self.checkout_session.store_shipping_methods(self.request.basket, methods)

		return methods

	def get_initial(self):
		initial = self.checkout_session.new_shipping_address_fields()
		if initial:
			initial = initial.copy()
			# Convert the primary key stored in the session into a Country
			# instance
			try:
				initial['country'] = Country.objects.get(
					iso_3166_1_a2=initial.pop('country_id'))
			except Country.DoesNotExist:
				# Hmm, the previously selected Country no longer exists. We
				# ignore this.
				pass
		return initial

	def shipping_method_form_valid(self, form):
		# Save the code for the chosen shipping method in the session
		# and continue to the next step.
		if not form.is_valid() and form.errors:
			print(f'\n *** form.errors: {form.errors}')
			return False

		self.checkout_session.use_shipping_method(form.cleaned_data['method_code'])
		return True

	def form_valid(self, form, option=None):

		# Store the address details in the session and redirect to next step
		address_fields = dict((k, v) for (k, v) in form.instance.__dict__.items() if not k.startswith('_'))
		self.checkout_session.ship_to_new_address(address_fields)
		return super().form_valid(form)

	## checks validity of zipcode or city + state
	## required: country? zip-code OR city+state
	def geolocation_is_valid(self):
		return True

	def get(self, request, *args, **kwargs):
		status_code = 302

		if request.is_ajax():
			status_code = 400

			# need some kind of check here to see if shipping methods should be returned
			# need another check to see if shipping methods should have changed, i.e
			if not hasattr(self, '_methods'):
				self._methods = self.get_available_shipping_methods() ## must be called prior to super().get()

			data = {'shipping_methods':[]}

			if self.geolocation_is_valid():
				## attempt to get shipping methods available based on geolocation

				status_code = 200
				for method in self._methods:
					data['shipping_methods'].append({'name': method.name, 'cost': method.calculate(self.request.basket).incl_tax, 'code':method.code})

				response = JsonResponse(data)

		else:
		# return a redirect since none of these urls should be called directly
			response = redirect(reverse_lazy('checkout:checkout'))

		response.status_code = status_code
		return response

	def get_available_addresses(self):
		return self.request.user.addresses.filter(
			country__is_shipping_country=True).order_by(
			'-is_default_for_shipping')

	def get_form_kwargs(self):
		print("\n *** get_form_kwargs() ShippingView *** \n")
		kwargs = super().get_form_kwargs()
		# kwargs.update({'methods':self._methods})
		return kwargs

	## should validate both shipping method and shipping address forms
	def post(self, request, *args, **kwargs):
		# super().get_context_data(*args, **kwargs)
		status_code = 400
		response = super().post(request, *args, **kwargs)

		if request.is_ajax():

			# shipping_address_data,shipping_method_data = {},{}

			# qd = request.POST.dict()
			shipping_method_code = request.POST.get('method_code', None)
			shipping_method_code = shipping_method_code if shipping_method_code else self.checkout_session.shipping_method_code
			# shipping_method_data.update({'csrfmiddlewaretoken': [qd['csrfmiddlewaretoken']], 'method_code': shipping_method_code})
			# shipping_address_data.update(qd)

			# shipping_address_form = ShippingAddressForm(shipping_address_data, *args, **kwargs)
			shipping_address_form = ShippingAddressForm(request.POST)

			# for item in request.session.items():
			# 	print('session item: ', item)

			if not hasattr(self, '_methods'):
				shipping_methods = self.get_available_shipping_methods()
				print('shipping_methods: ', shipping_methods, '\n')
				if not shipping_methods:
					shipping_methods = self.checkout_session.get_stored_shipping_methods()

				self._methods = shipping_methods ## must be called prior to super().get()

			data = {'shipping_methods':[], 'section': 'shipping'}

			# shipping_method_form = ShippingMethodForm(shipping_method_data, methods=self._methods)

			shipping_method_form = ShippingMethodForm(request.POST, methods=self._methods)

			if all([shipping_address_form.is_valid(), self.shipping_method_form_valid(shipping_method_form)]):

				status_code = 200
				country = shipping_address_form.cleaned_data['country']

				context_data = self.get_context_data(*args, **kwargs)
				shipping_address_obj = self.get_shipping_address(self.request.basket)

				# full_name = f"{shipping_address_form.cleaned_data['first_name']} {shipping_address_form.cleaned_data['last_name']}"

				data['shipping_charge'] = context_data['shipping_charge'].incl_tax

			response = JsonResponse(data)

		response.status_code = status_code
		return response



class AdditionalInfoView(CheckoutSessionMixin, generic.FormView):
	template_name = 'dehy/checkout/checkout_v2.html'
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured',
		'check_shipping_data_is_captured'
	]
	success_url = reverse_lazy('checkout:billing')
	template_name = "dehy/checkout/checkout_v2.html"
	form_class = AdditionalInfoForm

	def get(self, request, *args, **kwargs):
		status_code = 302
		response = super().get(request,*args, **kwargs)
		if request.is_ajax():
			status_code = 400
			pass
		else:
			# return a redirect since none of these urls should be called directly
			response = redirect(reverse_lazy('checkout:checkout'))

		response.status_code = status_code
		return response

	def post(self, request, *args, **kwargs):
		status_code = 400
		response = super().post(request,*args, **kwargs)
		data = {'section': 'additional_info'}
		if request.is_ajax():
			form = self.form_class(request.POST)


			if self.form_valid(form) and form.is_valid():

				form.cleaned_data['purchase_business_type']
				form.cleaned_data['business_name']

				additional_info_object,created = AdditionalInfoQuestionnaire.objects.update_or_create(
					id=self.checkout_session.get_questionnaire_response('id'),
					defaults={
						'purchase_business_type':form.cleaned_data['purchase_business_type'],
						'business_name':form.cleaned_data['business_name']
					}
				)

				self.checkout_session.set_questionnaire_response(additional_info_object)
				additional_info_object.save()
				data['section'] = 'additional_info'
				data['stripe_pkey'] = Facade().stripe.pkey

				status_code = 200

				response = JsonResponse(data)

		response.status_code = status_code
		return response

@method_decorator(csrf_exempt, name='dispatch')
class PlaceOrderView(views.PaymentDetailsView, CheckoutSessionMixin):
	template_name = 'dehy/checkout/checkout_v2.html'
	template_name_preview = 'dehy/checkout/checkout_v2.html'
	form_class = SubmitOrderForm

	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured',
		'check_shipping_data_is_captured'
	]

	pre_conditions = pre_conditions if not settings.DEBUG else []

	def dispatch(self, request, *args, **kwargs):
		# Assign the checkout session manager so it's available in all checkout
		# views.
		self.checkout_session = CheckoutSessionData(request)

		# Check if this view should be skipped
		try:
			self.check_skip_conditions(request)
		except exceptions.PassedSkipCondition as e:
			return http.HttpResponseRedirect(e.url)

		# Enforce any pre-conditions for the view.
		try:
			self.check_pre_conditions(request)
		except exceptions.FailedPreCondition as e:
			for message in e.messages:
				messages.warning(request, message)
			return http.HttpResponseRedirect(e.url)

		return super().dispatch(
			request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		status_code = 302
		super().get(request,*args, **kwargs)
		if request.is_ajax():
			status_code = 400
			pass
		else:
			# return a redirect since none of these urls should be called directly
			response = redirect(reverse_lazy('checkout:checkout'))

		response.status_code = status_code
		return response
	# needs to handle
	# need a way of referencing basket via stripe webhook
	# such as order number, basket id,
	def post(self, request, *args, **kwargs):

		print('request.POST: ', request.POST)

		print('request.is_ajax(): ', request.is_ajax())

		print(f'\ndir(request): {dir(request)}\n')

		# request came from client callback, handle it accordingly
		if request.is_ajax():

			# ensure the order has been placed
			# if it hasn't, place it here:

			# then return a redirect
			return self.get_success_url()


		# Request came from stripe webhook. This is expected and ideal
		# as we don't want to rely on client side callbacks to submit orders
		# to the backend.
		else:
			payload = request.body
			json_payload = json.loads(payload)
			data = json_payload.get('data', {})
			endpoint_secret = 'whsec_63c2ac70680ad9eb9ceddd981cb1be311fbd0ab114767d63c69c28f0374d8b42'
			# if we have the payment_intent then we can create the payment source

			event = None
			sig_header = request.headers['STRIPE_SIGNATURE']

			try:
				event = Facade().stripe.Webhook.construct_event(
					payload, sig_header, endpoint_secret
				)
			except ValueError as e:
				# Invalid payload
				raise e
			except Facade().stripe.error.SignatureVerificationError as e:
				# Invalid signature
				raise e

			# Handle the event
			if event['type'] == 'payment_intent.succeeded':
				status_code = 200
				payment_intent = event['data']['object']
				print('\n payment_intent (as created by stripe): ', payment_intent)
				print('\n dir(payment_intent): ', type(payment_intent))
				response = self.handle_place_order_submission(event)


			# ... handle other event types
			else:
				status_code = 400
				print('Unhandled event type {}'.format(event['type']))


		response = JsonResponse(data)
		response.status_code = 200
		return response

	def handle_place_order_submission(self, event):
		########################
		## list of stuff needed: user, basket, shipping_address, shipping_method, shipping_charge, billing_address, order_total
		########################

		if event.object=="payment_intent":

			# user

			# basket
			basket = basket_model.objects.get(id=event.metadata['basket_id'])
			order_id = event.metadata['order_id']
			order = Facade().stripe.Order.retrieve(order_id)

			# shipping_address
			# use shipping address form
			shipping_address = order.shipping_details
			# convert phone to phone_number
			# convert name to first_name + last_name
			# 'city' becomes 'line4'
			# 'postal_code' becomes 'postcode'

			# shipping_method
			#

			# shipping_charge
			shipping_charge = D(order.total_details.amount_shipping/100).quantize(TWOPLACES)

			# billing_address
			# use billing address form
			billing_address = order.billing_details

			# order_total
			order_total = D(order.amount_total/100).quantize(TWOPLACES)

			payment_kwargs = {
				'card': {
					'brand': event.charges.data.payment_method_details.card.brand,
					'exp': f"{event.charges.data.payment_method_details.card.exp_month:0>2}/{event.charges.data.payment_method_details.card.exp_year}",
					'last4': event.charges.data.payment_method_details.card.last4
				}
			}

		return self.submit(**self.build_submission())

	# noqa (too complex (10))
	def submit(self, user, basket, shipping_address, shipping_method, shipping_charge, billing_address, order_total, payment_kwargs=None, order_kwargs=None, surcharges=None):
		"""
		Submit a basket for order placement.
		The process runs as follows:
		 * Generate an order number
		 * Freeze the basket so it cannot be modified any more (important when
		   redirecting the user to another site for payment as it prevents the
		   basket being manipulated during the payment process).
		 * Attempt to take payment for the order
		   - If payment is successful, place the order
		   - If a redirect is required (e.g. PayPal, 3D Secure), redirect
		   - If payment is unsuccessful, show an appropriate error message
		:basket: The basket to submit.
		:payment_kwargs: Additional kwargs to pass to the handle_payment
						 method. It normally makes sense to pass form
						 instances (rather than model instances) so that the
						 forms can be re-rendered correctly if payment fails.
		:order_kwargs: Additional kwargs to pass to the place_order method
		"""
		if payment_kwargs is None:
			payment_kwargs = {}
		if order_kwargs is None:
			order_kwargs = {}
		order_number = basket.stripe_order_id
		self.checkout_session.set_order_number(order_number)
		logger.info("Order #%s: beginning submission process for basket #%d",
					basket.stripe_order_id, basket.id)

		self.freeze_basket(basket)
		self.checkout_session.set_submitted_basket(basket)

		# We define a general error message for when an unanticipated payment
		# error occurs.
		error_msg = _("A problem occurred while processing payment for this "
					  "order - no payment has been taken.  Please "
					  "contact customer services if this problem persists")

		signals.pre_payment.send_robust(sender=self, view=self)

		try:
			self.handle_payment(request, order_number, order_total, **payment_kwargs)
		except Exception as e:
			# Unhandled exception - as all payment is handling is client-side, this will be the only exception seen
			logger.exception(
				"Order #%s: unhandled exception while taking payment (%s)",
				order_number, e)
			self.restore_frozen_basket()
			return self.render_preview(self.request, error=error_msg, **payment_kwargs)

		signals.post_payment.send_robust(sender=self, view=self)

		# If all is ok with payment, try and place order
		logger.info("Order #%s: payment successful, placing order",
					order_number)
		try:
			return self.handle_order_placement(
				order_number, user, basket, shipping_address, shipping_method,
				shipping_charge, billing_address, order_total, surcharges=surcharges, **order_kwargs)


		except UnableToPlaceOrder as e:
			# It's possible that something will go wrong while trying to
			# actually place an order.  Not a good situation to be in as a
			# payment transaction may already have taken place, but needs
			# to be handled gracefully.
			msg = str(e)
			logger.error("Order #%s: unable to place order - %s",
						 order_number, msg, exc_info=True)
			self.restore_frozen_basket()
			return self.render_preview(
				self.request, error=msg, **payment_kwargs)
		except Exception as e:
			# Hopefully you only ever reach this in development
			logger.exception("Order #%s: unhandled exception while placing order (%s)", order_number, e)
			error_msg = _("A problem occurred while placing this order. Please contact customer services.")
			self.restore_frozen_basket()
			return self.render_preview(self.request, error=error_msg, **payment_kwargs)

	def handle_payment(self, order_number, total, *args, **kwargs):
		"""
		Handle any payment processing and record payment sources and events.
		This method is designed to be overridden within your project.  The
		default is to do nothing as payment is domain-specific.
		This method is responsible for handling payment and recording the
		payment sources (using the add_payment_source method) and payment
		events (using add_payment_event) so they can be
		linked to the order when it is saved later on.
		"""

		source_type,__ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)

		source = Source(
			source_type=source_type,
			currency=settings.STRIPE_CURRENCY,
			amount_allocated=total.incl_tax,
			amount_debited=total.incl_tax,
			reference=intent.id
		)

		self.add_payment_source(source)
		self.add_payment_event(PAYMENT_EVENT_PURCHASE, total.incl_tax)

	def handle_order_placement(self, order_number, user, basket, shipping_address, shipping_method,
		shipping_charge, billing_address, order_total, surcharges=None, **kwargs):

		"""
		Write out the order models and return the appropriate HTTP response
		We deliberately pass the basket in here as the one tied to the request
		isn't necessarily the correct one to use in placing the order.  This
		can happen when a basket gets frozen.
		"""
		order = self.place_order(
			order_number=order_number, user=user, basket=basket,
			shipping_address=shipping_address, shipping_method=shipping_method,
			shipping_charge=shipping_charge, order_total=order_total,
			billing_address=billing_address, surcharges=surcharges, **kwargs)
		basket.submit()
		return self.handle_successful_order(order)

	def handle_successful_order(self, order):
		"""
		Handle the various steps required after an order has been successfully
		placed.
		Override this view if you want to perform custom actions when an
		order is submitted.
		"""
		# Send confirmation message (normally an email)
		try:
			self.send_order_placed_email(order)

		except Exception as e:
			print('Error sending order placed email')

		# Flush all session data
		self.checkout_session.flush()

		# Save order id in session so thank-you page can load it
		self.request.session['checkout_order_id'] = order.id

		response = HttpResponseRedirect(self.get_success_url())
		self.send_signal(self.request, response, order)
		return response

	def send_order_placed_email(self, order):
		extra_context = self.get_message_context(order)
		dispatcher = OrderDispatcher(logger=logger)
		dispatcher.send_order_placed_email_for_user(order, extra_context)

	def payment_description(self, intent, order_number, total, **kwargs):

		return f"payment_intent:{intent['id']} customer: {intent['customer']}, card info: [last4:{intent['charges']['data'][0]['last4']}]"

	def payment_metadata(self, order_number, total, **kwargs):
		return {'order_number': order_number}

	def get_pre_conditions(self, request):
		return super().get_pre_conditions(request)

	def get_success_url(self):
		return reverse('checkout:thank_you')


class BillingView(views.PaymentDetailsView, CheckoutSessionMixin):

	template_name = 'dehy/checkout/checkout_v2.html'
	template_name_preview = 'dehy/checkout/checkout_v2.html'

	form_class = BillingAddressForm
	success_url = reverse_lazy('checkout:place_order')
	# These conditions are extended at runtime depending on whether we are in
	# 'preview' mode or not.
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured',
		'check_shipping_data_is_captured'
	]

	# If preview=True, then we render a preview template that shows all order
	# details ready for submission.

	preview = False

	def get(self, request, *args, **kwargs):
		status_code = 302
		super().get(request,*args, **kwargs)
		if request.is_ajax():
			status_code = 400
			pass
		else:
			# return a redirect since none of these urls should be called directly
			response = redirect(reverse_lazy('checkout:checkout'))

		response.status_code = status_code
		return response

	def post(self, request, *args, **kwargs):
		data = {}
		status_code = 400

		response = super().post(request, *args, **kwargs)
		context = self.get_context_data(*args, **kwargs)
		print('request.POST: ', request.POST)
		total = context['order_total']
		section = 'billing'
		form = self.form_class(request.POST)

		if self.preview:
			self.form_class = SubmitOrderForm
			form = SubmitOrderForm(request.POST)

		# payment_method_id = request.POST.get('payment_method_id', None)

		if not form.is_valid():
			print('form errors: ', form.errors)
			print('form non_field_errors: ', form.non_field_errors)

		if not request.is_ajax():
			print('\n request not ajax')
			print('form errors: ', form.errors)

		if request.is_ajax() and form.is_valid():
			status_code = 200
			cleaned_data = form.cleaned_data
			data['section'] = section
			# if self.preview:
			# 	print('\n handling order placement \n')
			# 	response = self.handle_place_order_submission(request)
			# 	if response.url is "/checkout/thank-you/":
			# 		status_code = 302
			# 		data['redirect'] = True
			# 		data['url'] = response.url
			# 		response = JsonResponse(data)
			# 	else:
			# 		status_code = 400

			if cleaned_data['same_as_shipping']:
				self.checkout_session.bill_to_shipping_address()

			address_fields = dict((k, v) for (k, v) in form.instance.__dict__.items() if not k.startswith('_'))

			phone_number = address_fields.get('phone_number').as_international if address_fields.get('phone_number', None) else None
			address_fields.update({'phone_number': phone_number, 'email': self.checkout_session.get_guest_email()})

			if phone_number:
				billing_details.update({'phone':phone_number})

			payment = Facade().update_and_process_order(request.basket, billing_details=address_fields)

			data['payment_intent_id'] = payment.payment_intent if type(payment.payment_intent) is str else payment.payment_intent.id
			data['client_secret'] = request.basket.payment_intent_client_secret
			data['stripe_pkey'] = Facade().stripe.pkey

			response = JsonResponse(data)

		response.status_code = status_code
		return response

	# def get_success_url(self):
	# 	return reverse('checkout:thank_you')
	#
	# def handle_payment(self, order_number, total, *args, **kwargs):
	# 	"""
	# 	Handle any payment processing and record payment sources and events.
	# 	This method is designed to be overridden within your project.  The
	# 	default is to do nothing as payment is domain-specific.
	# 	This method is responsible for handling payment and recording the
	# 	payment sources (using the add_payment_source method) and payment
	# 	events (using add_payment_event) so they can be
	# 	linked to the order when it is saved later on.
	# 	"""
	# 	context = self.get_context_data(*args, **kwargs)
	# 	total = context['order_total']
	#
	# 	form = self.form_class(request.POST)
	# 	# cleaned_data = form.cleaned_data
	#
	# 	if payment_intent_id:
	# 		setup_future_usage = None
	# 		customer = None
	# 		if hasattr(form, 'cleaned_data') and form.cleaned_data['create_new_account']:
	# 			## create a new user account
	# 			if cleaned_data['remember_payment_info'] and payment_method_id:
	# 				## save the user's payment information and attach it to the account
	# 				customer = Facade().update_or_create_customer(
	# 					checkout_session=self.checkout_session,
	# 					email='',#get the email the user entered earlier
	# 					payment_method=payment_method_id
	# 				)
	#
	#
	# 	intent = Facade().payment_intent_confirm(
	# 		payment_intent_id=payment_intent_id,
	# 		total=total,
	# 		payment_method_id=payment_method_id,
	# 		client_secret=self.checkout_session.get_stripe_client_secret(),
	# 		metadata=self.payment_metadata(order_number, total, **kwargs)
	# 	)
	#
	# 	# description = self.payment_description(intent, order_number, total, **kwargs)
	#
	#
	# 	source_type,__ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)
	#
	# 	source = Source(
	# 		source_type=source_type,
	# 		currency=settings.STRIPE_CURRENCY,
	# 		amount_allocated=total.incl_tax,
	# 		amount_debited=total.incl_tax,
	# 		reference=intent.id
	# 	)
	#
	# 	self.add_payment_source(source)
	#
	# 	self.add_payment_event(PAYMENT_EVENT_PURCHASE, total.incl_tax)
	#
	# def handle_order_placement(self, order_number, user, basket, shipping_address, shipping_method,
	# 	shipping_charge, billing_address, order_total, surcharges=None, **kwargs):
	#
	# 	"""
	# 	Write out the order models and return the appropriate HTTP response
	# 	We deliberately pass the basket in here as the one tied to the request
	# 	isn't necessarily the correct one to use in placing the order.  This
	# 	can happen when a basket gets frozen.
	# 	"""
	# 	order = self.place_order(
	# 		order_number=order_number, user=user, basket=basket,
	# 		shipping_address=shipping_address, shipping_method=shipping_method,
	# 		shipping_charge=shipping_charge, order_total=order_total,
	# 		billing_address=billing_address, surcharges=surcharges, **kwargs)
	# 	basket.submit()
	# 	return self.handle_successful_order(order)
	#
	# def handle_successful_order(self, order):
	# 	"""
	# 	Handle the various steps required after an order has been successfully
	# 	placed.
	# 	Override this view if you want to perform custom actions when an
	# 	order is submitted.
	# 	"""
	# 	# Send confirmation message (normally an email)
	# 	try:
	# 		self.send_order_placed_email(order)
	#
	# 	except Exception as e:
	# 		print('Error sending order placed email')
	#
	# 	# Flush all session data
	# 	self.checkout_session.flush()
	#
	# 	# Save order id in session so thank-you page can load it
	# 	self.request.session['checkout_order_id'] = order.id
	#
	# 	response = HttpResponseRedirect(self.get_success_url())
	# 	self.send_signal(self.request, response, order)
	# 	return response
	#
	# def send_order_placed_email(self, order):
	# 	extra_context = self.get_message_context(order)
	# 	dispatcher = OrderDispatcher(logger=logger)
	# 	dispatcher.send_order_placed_email_for_user(order, extra_context)
	#
	# def handle_place_order_submission(self):
	# 	"""
	# 	Handle a request to place an order.
	# 	This method is normally called after the customer has clicked "place
	# 	order" on the preview page. It's responsible for (re-)validating any
	# 	form information then building the submission dict to pass to the
	# 	`submit` method.
	# 	If forms are submitted on your payment details view, you should
	# 	override this method to ensure they are valid before extracting their
	# 	data into the submission dict and passing it onto `submit`.
	# 	"""
	# 	return self.submit(**self.build_submission())
	#
	# # noqa (too complex (10))
	# def submit(self, user, basket, shipping_address, shipping_method, shipping_charge, billing_address, order_total, payment_kwargs=None, order_kwargs=None, surcharges=None):
	# 	"""
	# 	Submit a basket for order placement.
	# 	The process runs as follows:
	# 	 * Generate an order number
	# 	 * Freeze the basket so it cannot be modified any more (important when
	# 	   redirecting the user to another site for payment as it prevents the
	# 	   basket being manipulated during the payment process).
	# 	 * Attempt to take payment for the order
	# 	   - If payment is successful, place the order
	# 	   - If a redirect is required (e.g. PayPal, 3D Secure), redirect
	# 	   - If payment is unsuccessful, show an appropriate error message
	# 	:basket: The basket to submit.
	# 	:payment_kwargs: Additional kwargs to pass to the handle_payment
	# 					 method. It normally makes sense to pass form
	# 					 instances (rather than model instances) so that the
	# 					 forms can be re-rendered correctly if payment fails.
	# 	:order_kwargs: Additional kwargs to pass to the place_order method
	# 	"""
	# 	if payment_kwargs is None:
	# 		payment_kwargs = {}
	# 	if order_kwargs is None:
	# 		order_kwargs = {}
	#
	# 	# Taxes must be known at this point
	# 	assert basket.is_tax_known, (
	# 		"Basket tax must be set before a user can place an order")
	# 	assert shipping_charge.is_tax_known, (
	# 		"Shipping charge tax must be set before a user can place an order")
	#
	# 	# We generate the order number first as this will be used
	# 	# in payment requests (ie before the order model has been
	# 	# created).  We also save it in the session for multi-stage
	# 	# checkouts (e.g. where we redirect to a 3rd party site and place
	# 	# the order on a different request).
	# 	self.checkout_session.set_order_number(basket.stripe_order_id)
	# 	logger.info("Order #%s: beginning submission process for basket #%d",
	# 				basket.stripe_order_id, basket.id)
	#
	# 	# Freeze the basket so it cannot be manipulated while the customer is
	# 	# completing payment on a 3rd party site.  Also, store a reference to
	# 	# the basket in the session so that we know which basket to thaw if we
	# 	# get an unsuccessful payment response when redirecting to a 3rd party
	# 	# site.
	#
	# 	self.freeze_basket(basket)
	# 	self.checkout_session.set_submitted_basket(basket)
	#
	# 	# We define a general error message for when an unanticipated payment
	# 	# error occurs.
	# 	error_msg = _("A problem occurred while processing payment for this "
	# 				  "order - no payment has been taken.  Please "
	# 				  "contact customer services if this problem persists")
	#
	# 	signals.pre_payment.send_robust(sender=self, view=self)
	#
	# 	try:
	# 		self.handle_payment(request, order_number, order_total, **payment_kwargs)
	# 	except RedirectRequired as e:
	# 		# Redirect required (e.g. PayPal, 3DS)
	# 		print('\n RedirectRequired \n')
	#
	# 		logger.info("Order #%s: redirecting to %s", order_number, e.url)
	# 		return HttpResponseRedirect(e.url)
	# 	except UnableToTakePayment as e:
	# 		# Something went wrong with payment but in an anticipated way.  Eg
	# 		# their bankcard has expired, wrong card number - that kind of
	# 		# thing. This type of exception is supposed to set a friendly error
	# 		# message that makes sense to the customer.
	# 		print('\n UnableToTakePayment \n')
	#
	# 		msg = str(e)
	# 		logger.warning(
	# 			"Order #%s: unable to take payment (%s) - restoring basket",
	# 			order_number, msg)
	# 		self.restore_frozen_basket()
	#
	# 		# We assume that the details submitted on the payment details view
	# 		# were invalid (e.g. expired bankcard).
	# 		return self.render_payment_details(
	# 			self.request, error=msg, **payment_kwargs)
	# 	except PaymentError as e:
	# 		# A general payment error - Something went wrong which wasn't
	# 		# anticipated.  Eg, the payment gateway is down (it happens), your
	# 		# credentials are wrong - that king of thing.
	# 		# It makes sense to configure the checkout logger to
	# 		# mail admins on an error as this issue warrants some further
	# 		# investigation.
	# 		print('\n PaymentError \n')
	#
	# 		msg = str(e)
	# 		logger.error("Order #%s: payment error (%s)", order_number, msg,
	# 					 exc_info=True)
	# 		self.restore_frozen_basket()
	# 		return self.render_preview(
	# 			self.request, error=error_msg, **payment_kwargs)
	# 	except Exception as e:
	# 		# Unhandled exception - hopefully, you will only ever see this in
	# 		# development...
	# 		logger.exception(
	# 			"Order #%s: unhandled exception while taking payment (%s)",
	# 			order_number, e)
	# 		self.restore_frozen_basket()
	# 		return self.render_preview(
	# 			self.request, error=error_msg, **payment_kwargs)
	#
	# 	signals.post_payment.send_robust(sender=self, view=self)
	#
	# 	# If all is ok with payment, try and place order
	# 	logger.info("Order #%s: payment successful, placing order",
	# 				order_number)
	# 	try:
	# 		return self.handle_order_placement(
	# 			order_number, user, basket, shipping_address, shipping_method,
	# 			shipping_charge, billing_address, order_total, surcharges=surcharges, **order_kwargs)
	#
	#
	# 	except UnableToPlaceOrder as e:
	# 		# It's possible that something will go wrong while trying to
	# 		# actually place an order.  Not a good situation to be in as a
	# 		# payment transaction may already have taken place, but needs
	# 		# to be handled gracefully.
	# 		msg = str(e)
	# 		logger.error("Order #%s: unable to place order - %s",
	# 					 order_number, msg, exc_info=True)
	# 		self.restore_frozen_basket()
	# 		return self.render_preview(
	# 			self.request, error=msg, **payment_kwargs)
	# 	except Exception as e:
	# 		# Hopefully you only ever reach this in development
	# 		logger.exception("Order #%s: unhandled exception while placing order (%s)", order_number, e)
	# 		error_msg = _("A problem occurred while placing this order. Please contact customer services.")
	# 		self.restore_frozen_basket()
	# 		return self.render_preview(self.request, error=error_msg, **payment_kwargs)
	#
	# def payment_description(self, intent, order_number, total, **kwargs):
	#
	# 	return f"payment_intent:{intent['id']} customer: {intent['customer']}, card info: [last4:{intent['charges']['data'][0]['last4']}]"
	#
	# def payment_metadata(self, order_number, total, **kwargs):
	# 	return {'order_number': order_number}
	#
class ThankYouView(views.ThankYouView):
	"""
	Displays the 'thank you' page which summarises the order just submitted.
	"""
	template_name = 'dehy/checkout/thank_you.html'
