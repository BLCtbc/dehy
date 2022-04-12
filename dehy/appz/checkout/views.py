from oscar.apps.checkout import signals, views
from oscar.apps.payment import models
from oscar.core.loading import get_class, get_classes, get_model
from oscar.apps.checkout import exceptions
from oscar.core import prices

from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict, JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views import generic
from decimal import Decimal as D
TWO_PLACES = D(10)**-2
FOUR_PLACES = D(10)**-4

from .facade import Facade
Facade = Facade()

from urllib.parse import quote
import datetime, json, logging, requests, sys, xmltodict, time

from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN

BasketView = get_class('basket.views', 'BasketView')
Basket = get_model('basket', 'Basket')
Order = get_model('order', 'Order')

User = get_model('generic', 'User')

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

from dehy.appz.order.models import BillingAddress

logger = logging.getLogger('oscar.checkout')

def calculate_tax(price, rate):
	tax = D(price*rate)
	return tax.quantize(FOUR_PLACES)

def Deb(msg=''):
	print(f"Debug {sys._getframe().f_back.f_lineno}: {msg}")

def get_city_and_state(postcode=None):
	# try:
	logger.debug(f'USPS API: Attempting to retrieve city/state information ({postcode})')
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
			logger.debug(f"USPS API [Error]: ({postcode}) {usps_response['ZipCode']['Error']}")

		else:
			data['city'] = usps_response['ZipCode']['City']
			data['line4'] = usps_response['ZipCode']['City']
			data['state'] = usps_response['ZipCode']['State']

		return data

# stripe webhook handler
@csrf_exempt
@require_POST
def webhook_submit_order(request):
	print('\n --- caught a webhook --- ', datetime.datetime.now())

	place_order_view = PlaceOrderView(request=request)

	payload = request.body
	# endpoint_secret = 'whsec_63c2ac70680ad9eb9ceddd981cb1be311fbd0ab114767d63c69c28f0374d8b42'

	event = None
	sig_header = request.headers['STRIPE_SIGNATURE']

	try:
		event = Facade.stripe.Webhook.construct_event(
			payload, sig_header, Facade.STRIPE_ORDER_SUBMITTED_SIGNING_SECRET
		)

	except ValueError as e:
		# Invalid payload
		msg = 'Stripe webhook: Invalid payload' + str(e)
		logger.error(msg)
		raise e

	except Facade.stripe.error.SignatureVerificationError as e:
		msg = 'Stripe webhook: ⚠️  Webhook signature verification failed.' + str(e)
		logger.error(msg)

		response = JsonResponse({})
		response.status_code = 400
		return response

	if event['type'] == 'order.payment_completed' :
		print('Event type {}'.format(event['type']))

		order = event['data']['object']
		basket = get_object_or_404(Basket, id=order.metadata.get('basket_id'))
		order = Facade.stripe.Order.retrieve(order.id, expand=['customer', 'payment.payment_intent', 'line_items'])
		place_order_view.handle_place_order_submission(basket, order)
		response = JsonResponse({})
		response.status_code = 200
		return response

	# Handle the event
	# if event['type'] == 'payment_intent.succeeded' or event['type'] == 'order.completed':
	# 	print('Event type {}'.format(event['type']))
	# 	payment_intent = event['data']['object']
	#
	# 	basket = get_object_or_404(Basket, id=payment_intent.metadata.get('basket_id'))
	# 	order_id = payment_intent.metadata.get('order_id', None) or f"order_{basket.stripe_order_id}"
	#
	# 	order = Facade.stripe.Order.retrieve(order_id, expand=['customer', 'payment.payment_intent', 'line_items'])
	# 	place_order_view.handle_place_order_submission(basket, order)
	#
	# 	response = JsonResponse({})
	# 	response.status_code = 200
	# 	return response

	# if event['type'] == 'order.payment_succeeded':
	# 	order = event['data']['object']


	# ... handle other event types
	else:
		msg = f"Unhandled event type {event['type']}"
		logger.debug(msg)
		status_code = 400

	response = JsonResponse({})
	response.status_code = status_code
	return response


def ajax_set_shipping_method(request):

	data = {}
	status_code = 400

	checkout_session = CheckoutSessionData(request)
	method_code = request.POST.get('method_code', None)
	shipping_methods = checkout_session.get_stored_shipping_methods()

	method_codes = [method.code for method in shipping_methods]
	if method_code and method_code in method_codes:
		selected_method = list(filter(lambda x: getattr(x, 'code', None)==method_code, shipping_methods))[0]
		status_code = 200
		checkout_session.use_shipping_method(method_code)

		order = Facade.update_or_create_order(request.basket, shipping_method={'cost':selected_method.calculate(request.basket).excl_tax, 'code':selected_method.code, 'name':selected_method.name})
		checkout_session.set_order_number(str(order.id).replace("order_", ""))

		data['subtotal'] = str(D(order.amount_subtotal/100).quantize(TWO_PLACES))
		data['total_tax'] = str(D(order.total_details.amount_tax/100).quantize(TWO_PLACES))
		data['shipping_charge'] = str(D(order.total_details.amount_shipping/100).quantize(TWO_PLACES))
		data['order_total'] = str(D(order.amount_total/100).quantize(TWO_PLACES))


	response = JsonResponse(data)
	response.status_code = status_code
	return response


def get_shipping_methods(request, shipping_fields, frontend_formatted=False, return_status_code=False):

	shipping_methods, methods = [], []
	if type(shipping_fields) is str:
		shipping_fields = json.loads(shipping_fields)

	if not shipping_fields.get('country', None):
		# shipping_fields['country'] = Country.objects.get(iso_3166_1_a2=shipping_fields['country_id'])
		shipping_fields['country'] = shipping_fields.get('country_id')

	shipping_address_form = CountryAndPostcodeForm(shipping_fields)
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
	else:
		print('\n shipping_address_form errors: ', shipping_address_form.errors)
	return methods

# also 'corrects' city and state based on postcode
def ajax_get_shipping_methods(request):
	data = {}
	status_code = 400

	# try:
	post_data = request.POST.copy()

	if post_data.get('postcode', None):
		city_and_state_data = get_city_and_state(request.POST.get('postcode'))
		post_data.update(city_and_state_data)
		data.update(city_and_state_data)


	checkout_session = CheckoutSessionData(request)
	shipping_address_form = CountryAndPostcodeForm(post_data)

	if not shipping_address_form.is_valid():
		print(f'\n form.errors: {shipping_address_form.errors}')
		data['errors'] = shipping_address_form.errors.as_json()


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


			order = Facade.update_or_create_order(request.basket, shipping_fields=address_fields, shipping_method={'cost':data['shipping_charge'], 'code':data['shipping_methods'][0]['code'], 'name':data['shipping_methods'][0]['name']})

			checkout_session.set_order_number(str(order.id).replace("order_", ""))
			data['order_client_secret'] = order.client_secret

			data['order_total'] = str(D(order.amount_total/100).quantize(TWO_PLACES))
			data['subtotal'] = str(D(order.amount_subtotal/100).quantize(TWO_PLACES))
			data['total_tax'] = str(D(order.total_details.amount_tax/100).quantize(TWO_PLACES))


	response = JsonResponse(data)
	response.status_code = status_code
	return response


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

	def get(self, request, *args, **kwargs):

		response = super().get(request, *args, **kwargs)
		self.checkout_session.reset_shipping_data()

		basket_view = BasketView.as_view()(request)

		order = Facade.update_or_create_order(request.basket)

		response.context_data.update({
			'form': self.form_class(),
			'basket_summary_context_data': basket_view.context_data,
			'is_shipping_address_set': self.checkout_session.is_shipping_address_set(),
			'is_shipping_method_set':self.checkout_session.is_shipping_method_set(request.basket)
		})
		return response

	def post(self, request, *args, **kwargs):

		data = {}
		status_code = 400
		form = self.form_class(request, request.POST)
		response = super().post(request, *args, **kwargs)

		if request.is_ajax() and form.is_valid():

			## get or create the stripe customer object
			email = form.cleaned_data['username']
			customer = Facade.get_or_create_customer(email)
			request.basket.stripe_customer_id = customer.id
			request.basket.save()

			if request.user.is_authenticated:
				request.user.stripe_customer_id = customer.id
				request.user.save()

			status_code = 200
			data['section'] = 'user_info'

			response = JsonResponse(data)


		response.status_code = status_code
		return response

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


	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		email = self.checkout_session.get_guest_email()
		if email:
			kwargs['initial'] = {
				'username': email,
			}
		return kwargs




class ShippingView(CheckoutSessionMixin, generic.FormView):
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured'
	]
	success_url = reverse_lazy('checkout:additional_info')
	template_name = "dehy/checkout/checkout_v2.html"
	form_class = ShippingAddressForm

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


			if not hasattr(self, '_methods'):
				shipping_methods = self.get_available_shipping_methods()
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
				data['shipping_charge'] = context_data['shipping_charge'].incl_tax

			response = JsonResponse(data)

		response.status_code = status_code
		return response

	def get_available_addresses(self):

		return self.request.user.addresses.filter(
			country__is_shipping_country=True).order_by(
			'-is_default_for_shipping')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['methods'] = self._methods
		if self.request.user.is_authenticated:
			# Look up address book data
			ctx['addresses'] = self.get_available_addresses()

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



	def get_available_addresses(self):
		return self.request.user.addresses.filter(
			country__is_shipping_country=True).order_by(
			'-is_default_for_shipping')

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		# kwargs.update({'methods':self._methods})
		return kwargs



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

				data['stripe_pkey'] = Facade.stripe.pkey

				status_code = 200

				response = JsonResponse(data)

		response.status_code = status_code
		return response


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

	preview = False

	def get(self, request, *args, **kwargs):
		status_code = 302
		super().get(request,*args, **kwargs)
		if request.is_ajax():
			status_code = 400
			pass
		else:
			response = redirect(reverse_lazy('checkout:checkout'))

		response.status_code = status_code
		return response

	def post(self, request, *args, **kwargs):
		data = {'section': 'billing'}
		status_code = 400

		response = super().post(request, *args, **kwargs)
		context = self.get_context_data(*args, **kwargs)
		total = context['order_total']
		form = self.form_class(request.POST)

		if not form.is_valid():
			print('form errors: ', form.errors)
			print('form non_field_errors: ', form.non_field_errors)

		if not request.is_ajax():
			print('form errors: ', form.errors)

		if request.is_ajax() and form.is_valid():
			status_code = 200
			cleaned_data = form.cleaned_data

			if cleaned_data['same_as_shipping']:
				self.checkout_session.ship_to_new_address(self.checkout_session.new_shipping_address_fields())
				self.checkout_session.bill_to_shipping_address()

			address_fields = dict((k, v) for (k, v) in form.instance.__dict__.items() if not k.startswith('_'))

			phone_number = address_fields.get('phone_number').as_international if address_fields.get('phone_number', None) else None
			address_fields.update({'email': self.checkout_session.get_guest_email()})

			if phone_number:
				address_fields.update({'phone':phone_number})

			if isinstance(address_fields.get('country', None), Country):
				address_fields['country'] = address_fields['country'].iso_3166_1_a2

			# order = Facade.update_and_process_order(request.basket, billing_fields=address_fields)
			billing_details = Facade.coerce_to_address_object(address_fields)
			stripe_order_id = f"order_{request.basket.stripe_order_id}"
			order = Facade.stripe.Order.modify(stripe_order_id, billing_details=billing_details)
			payment = order.payment

			data['order_client_secret'] = order.client_secret
			data['stripe_pkey'] = Facade.stripe.pkey
			response = JsonResponse(data)

		response.status_code = status_code


		return response

class PlaceOrderView(views.PaymentDetailsView, CheckoutSessionMixin):
	template_name = 'dehy/checkout/checkout_v2.html'
	template_name_preview = 'dehy/checkout/checkout_v2.html'
	success_url = reverse_lazy('checkout:place_order')
	form_class = SubmitOrderForm
	skip_conditions = None
	pre_conditions = [
		'check_basket_is_not_empty',
		'check_basket_is_valid',
		'check_user_email_is_captured',
		'check_shipping_data_is_captured'
	]
	preview = True

	pre_conditions = pre_conditions if not settings.DEBUG else []

	def skip_unless_payment_is_required(self, request):
		# overwriting this method because payment is ALWAYS required... for now
		return True

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

	def post(self, request, *args, **kwargs):
		data = {}
		# request came from client callback, handle it accordingly
		if request.is_ajax():

			basket_id = self.get_submitted_basket_id()

			# order successfully placed
			if request.basket.is_submitted():
				data['order_number'] = self.get_order_number() or request.basket.stripe_order_id
				pass
			# uh oh...
			else:
				pass
			# ensure the order has been placed
			# if it hasn't, place it here:

			# then return a redirect
			# return self.get_success_url()
			response = JsonResponse(data)
			response.status_code = 200

		else:
			response = super().post(request, *args, **kwargs)

		return response

	# Coerces a Stripe address object into a structure acceptable for an address form
	def coerce_from_address_object(self, address_details):
		# 'phone' becomes 'phone_number'
		# convert name to first_name + last_name
		# 'city' becomes 'line4'
		# 'postal_code' becomes 'postcode'
		first_name,last_name = address_details.name.split(" ")
		country_obj = Country.objects.get(iso_3166_1_a2=address_details.address.country)
		address = {
			'first_name': first_name,
			'last_name': last_name,
			'line1': address_details.address.line1,
			'line4': address_details.address.city,
			'country': country_obj,
			'state': address_details.address.state,
			'postcode': address_details.address.postal_code,
		}
		if address_details.address.line2:
			address.update({'line2': address_details.address.line2})

		if address_details.phone:
			address.update({'phone_number':address_details.phone})

		return address

	def handle_place_order_submission(self, basket, order):

		basket._set_strategy(self.request.strategy)

		user = User.objects.get(id=basket.owner_id) if basket.owner_id else AnonymousUser()

		print('-- associated order: ', order)
		# shipping_address (should be an instance of ShippingAddressForm)
		# use shipping address form
		shipping_address = ShippingAddress(**self.coerce_from_address_object(order.shipping_details))

		# shipping_charge
		shipping_charge = prices.Price(
			currency=basket.currency,
			excl_tax=D(order.shipping_cost.amount_subtotal/100).quantize(TWO_PLACES),
			incl_tax=D(order.shipping_cost.amount_total/100).quantize(TWO_PLACES)
		)

		# shipping_method
		from dehy.appz.shipping.methods import BaseFedex
		shipping_method = BaseFedex(code=order.metadata['shipping_code'], name=order.metadata['shipping_name'], charge_excl_tax=shipping_charge, charge_incl_tax=shipping_charge)


		# billing_address (should be an instance of BillingAddress)
		billing_address = BillingAddress(**self.coerce_from_address_object(order.billing_details))

		# order_total
		order_total = prices.Price(
			currency=basket.currency,
			excl_tax=D(order.amount_subtotal/100).quantize(TWO_PLACES),
			incl_tax=D(order.amount_total/100).quantize(TWO_PLACES)
		)

		for line in basket.all_lines():

			stripe_line = list(filter(lambda x: x['product']==line.product.upc, order.line_items.data))[0]
			tax_rate = D(stripe_line['amount_tax']/stripe_line['amount_subtotal']).quantize(FOUR_PLACES)
			price_incl_tax = line.price_excl_tax + calculate_tax(line.price_excl_tax, tax_rate)
			line.purchase_info.price.tax = calculate_tax(line.price_excl_tax, tax_rate)
			line.save()
		# Need to put card info on the order info and then pass it along on
		# the order receipt + order receipt email

		payment_kwargs = {
			'total_tax': D(order.total_details.amount_tax/100).quantize(TWO_PLACES),
			'payment_intent_id': order.payment.payment_intent.id,
			'charge_id': order.payment.payment_intent.charges.data[0]['id'],
			'order_total': {
				'amount': D(order.payment.payment_intent.charges.data[0]['amount']/100).quantize(TWO_PLACES),
				'amount_captured': D(order.payment.payment_intent.charges.data[0]['amount_captured']/100).quantize(TWO_PLACES)
			},
			'card': {
				'brand': order.payment.payment_intent.charges.data[0]['payment_method_details']['card']['brand'],
				'exp': f"{order.payment.payment_intent.charges.data[0]['payment_method_details']['card']['exp_month']:0>2}/{order.payment.payment_intent.charges.data[0]['payment_method_details']['card']['exp_year']}",
				'last4': order.payment.payment_intent.charges.data[0]['payment_method_details']['card']['last4']
			}
		}

			# could update the customer info here

		email = order.customer.email if order.customer else order.billing_details.email
		order_kwargs = {'guest_email': email}

		order_details = {
			'user': user,
			'basket': basket,
			'shipping_address': shipping_address,
			'shipping_method': shipping_method,
			'shipping_charge': shipping_charge,
			'billing_address': billing_address,
			'order_total': order_total,
			'payment_kwargs': payment_kwargs,
			'order_kwargs': order_kwargs
		}

		return self.submit(**order_details)

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
		# self.checkout_session.set_order_number(order_number)
		logger.info("Order #%s: beginning submission process for basket #%d",
					basket.stripe_order_id, basket.id)

		self.freeze_basket(basket)
		# self.checkout_session.set_submitted_basket(basket)

		# We define a general error message for when an unanticipated payment
		# error occurs.
		error_msg = _("A problem occurred while processing payment for this "
					  "order - no payment has been taken.  Please "
					  "contact customer services if this problem persists")

		signals.pre_payment.send_robust(sender=self, view=self)

		try:
			self.handle_payment(order_number, order_total, **payment_kwargs)
		except Exception as e:
			# Unhandled exception - as all payment is handling is client-side, this will be the only exception seen
			print(f"\n -- Order #{order_number}: unhandled exception while taking payment: ({e})")
			logger.exception(
				"Order #%s: unhandled exception while taking payment (%s)",
				order_number, e)
			# self.restore_frozen_basket()
			# return self.render_preview(self.request, error=error_msg, **payment_kwargs)

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
			print(f"\n -- Order #{order_number}: unable to place order - ({msg})")
			logger.error("Order #%s: unable to place order - %s",
						 order_number, msg, exc_info=True)
			# self.restore_frozen_basket()
			# return self.render_preview(self.request, error=msg, **payment_kwargs)
		except Exception as e:
			# Hopefully you only ever reach this in development
			logger.exception("Order #%s: unhandled exception while placing order (%s)", order_number, e)
			error_msg = _("A problem occurred while placing this order. Please contact customer services.")
			# self.restore_frozen_basket()
			# return self.render_preview(self.request, error=error_msg, **payment_kwargs)

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
			reference=kwargs.get('payment_intent_id', None),
			label=f"{kwargs['card']['brand']} XXXX-{kwargs['card']['last4']}"
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
			print('Error sending order placed email: ', str(e))

		# Flush all session data
		try:
			self.checkout_session.flush()
		except AttributeError as e:
			print(e)

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



class ThankYouView(views.ThankYouView):
	"""
	Displays the 'thank you' page which summarises the order just submitted.
	"""
	template_name = 'dehy/checkout/thank_you.html'
	max_wait = 15
	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object is None:
			return redirect(settings.OSCAR_HOMEPAGE)
		context = self.get_context_data(object=self.object)
		context.update({'lg_col_size': 10, 'md_col_size':"col-md-11"})
		return self.render_to_response(context)

	def get_object(self, queryset=None):

		order = None
		# We allow superusers to force an order thank-you page for testing
		if self.request.user.is_superuser:
			kwargs = {}
			if 'order_number' in self.request.GET:
				kwargs['number'] = self.request.GET['order_number']
			elif 'order_id' in self.request.GET:
				kwargs['id'] = self.request.GET['order_id']
			order = Order._default_manager.filter(**kwargs).first()
			print('super user order found: ', order)

		stripe_order_id = self.request.GET.get('order', None)
		order_client_secret = self.request.GET.get('order_client_secret', None)
		order_id = ''

		if stripe_order_id and order_client_secret:
			order_id = stripe_order_id.replace("order_", "")
			basket = Basket._default_manager.filter(stripe_order_id=order_id)

			if basket:
				basket = basket.first()

				submitted = basket.is_submitted
				# print(f'\n basket.is_submitted: {submitted}')
				start_time = time.time()
				while not submitted:
					time.sleep(0.5)
					basket.refresh_from_db()
					submitted = basket.is_submitted

					print(f'\n basket.is_submitted: {submitted}')

					if time.time() - start_time > self.max_wait:
						print('\n *** max wait time exceeded: ', time.time() - start_time)
						return order


				order_ = Order._default_manager.filter(number=order_id, basket=basket)
				if order_:
					order = order_.first()


		return order