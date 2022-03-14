from oscar.apps.checkout import signals, views
from oscar.apps.payment import models
from oscar.core.loading import get_class, get_classes, get_model

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views import generic

from .facade import Facade

from urllib.parse import quote
import json, logging, sys

from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN

BasketView = get_class('basket.views', 'BasketView')

BillingAddressForm, StripeTokenForm, ShippingAddressForm, ShippingMethodForm, UserInfoForm, AdditionalInfoForm, SubmitOrderForm \
	= get_classes('checkout.forms', ['BillingAddressForm', 'StripeTokenForm', 'ShippingAddressForm', 'ShippingMethodForm', 'UserInfoForm', 'AdditionalInfoForm', 'PurchaseConfirmationForm'])

# BankcardForm, BillingAddressForm \
# 	= get_classes('payment.forms', ['BankcardForm', 'BillingAddressForm'])
RedirectRequired, UnableToTakePayment, PaymentError = get_classes('payment.exceptions', ['RedirectRequired','UnableToTakePayment','PaymentError'])

Repository = get_class('shipping.repository', 'Repository')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
OrderDispatcher = get_class('order.utils', 'OrderDispatcher')
AdditionalInfoQuestionnaire = get_class('dehy.appz.generic.models', 'AdditionalInfoQuestionnaire')
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')

SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')
Country = get_model('address', 'Country')

logger = logging.getLogger('oscar.checkout')
# def get_form(request):
# 	status_code = 400
# 	if request.is_ajax() and request.method=="GET":
# 		form_name = request.GET.get('name', None)
# 		if form_name:
#

from datetime import datetime
old_print = print

def timestamped_print(*args, **kwargs):
	old_print(datetime.now(), *args, **kwargs)

print = timestamped_print

def Deb(msg=''):
	print(f"Debug {sys._getframe().f_back.f_lineno}: {msg}")



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
		print(f'\n context_data (index): {context_data}')
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
		print(request.POST)
		form = self.form_class(request, request.POST)
		response = super().post(request, *args, **kwargs)

		if request.is_ajax() and form.is_valid():
			# self.pre_conditions += ['check_user_email_is_captured']
			self.check_pre_conditions(request)
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
		print('\n*** get() index ***')
		form_structure = self.get_form_structure(self.form_class)

		print(f"\n dir(request): {dir(request)}")
		# print(f"\n dir(request.session): {dir(request)}")
		print(f"\n dir(self): {dir(request.basket)}")
		print(f"\n dir(self.checkout_session): {dir(self.checkout_session)}")

		print(f"\n is_shipping_method_set: {self.checkout_session.is_shipping_method_set(request.basket)}")

		response = super().get(request, *args, **kwargs)
		basket_view = BasketView.as_view()(request)
		print(f"\n self. basket_view.context_data: {basket_view.context_data}")

		# basket_summary_context = basket_view.get_context_data(request, *args, **kwargs)

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

	# def setup(self, request, *args, **kwargs):
	# 	print(f'\n *** setup()')
	# 	return super().setup(request, *args, **kwargs)
	#
	# def dispatch(self, request, *args, **kwargs):
	# 	print(f'\n *** dispatch()')
	# 	return super().dispatch(request, *args, **kwargs)

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
		return Repository().get_shipping_methods(
			basket=self.request.basket, user=self.request.user,
			shipping_addr=self.get_shipping_address(self.request.basket),
			request=self.request)

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
	def geolocation_is_valid(self, request):
		return True

	def get(self, request, *args, **kwargs):
		print('\n*** get() ShippingView ***')
		status_code = 302
		if request.is_ajax():
			status_code = 400

			# need some kind of check here to see if shipping methods should be returned
			# need another check to  see if shipping methods should have changed, i.e
			if not hasattr(self, '_methods'):
				print('\n *** _methods not found *** \n')
				self._methods = self.get_available_shipping_methods() ## must be called prior to super().get()

			## indicates shipping methods haven't changed (DOESNT WORK)
			elif self._methods == self.get_available_shipping_methods():
				status_code = 204

			# response = super().get(request, *args, **kwargs) ## also calls get_context_data
			context_data = self.get_context_data()

			data = {'shipping_methods':[]}

			if self.geolocation_is_valid(request):
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
		print("\n *** post() ShippingView *** \n")
		print(f"\nrequest.session.modified: {request.session.modified}")
		self._methods = self.get_available_shipping_methods()
		data = {'section': 'shipping'}
		status_code = 400
		response = super().post(request, *args, **kwargs)
		if request.is_ajax():
			shipping_address_data,shipping_method_data = {},{}

			# self.pre_conditions += ['check_user_email_is_captured']
			self.check_pre_conditions(request)
			qd = request.POST.dict()
			shipping_method_data.update({'csrfmiddlewaretoken': [qd['csrfmiddlewaretoken']], 'method_code': qd.pop('method_code')})

			shipping_address_data.update(qd)
			shipping_method_form = ShippingMethodForm(shipping_method_data, methods=self._methods)
			shipping_address_form = ShippingAddressForm(shipping_address_data, *args, **kwargs)

			if all([shipping_address_form.is_valid(), self.shipping_method_form_valid(shipping_method_form)]):
				## return additional_info form structure
				status_code = 200
				country = shipping_address_form.cleaned_data['country']
				data['preview_elems'] = {
					'first_name': shipping_address_form.cleaned_data['first_name'],
					'last_name': shipping_address_form.cleaned_data['last_name'],
					'phone_number': shipping_address_form.cleaned_data['phone_number'].raw_input,
					'line1': shipping_address_form.cleaned_data['line1'],
					'line2': shipping_address_form.cleaned_data['line2'],
					'line4': shipping_address_form.cleaned_data['line4'],
					'state': shipping_address_form.cleaned_data['state'],
					'postcode': shipping_address_form.cleaned_data['postcode'],
					'country': shipping_address_form.cleaned_data['country'].printable_name,
					'shipping_method': shipping_method_form.cleaned_data['method_code'],
				}

				# client_secret = self.checkout_session.get_stripe_payment_intent()['id'] if self.checkout_session.is_stripe_payment_intent_set() else None

				full_name = f"{shipping_address_form.cleaned_data['first_name']} {shipping_address_form.cleaned_data['last_name']}"

				context_data = self.get_context_data(*args, **kwargs)
				shipping_address_obj = self.get_shipping_address(self.request.basket)

				shipping = {
					'address': {
						'city': shipping_address_obj.city,
						'country': shipping_address_obj.country,
						'line1': shipping_address_obj.line1,
						'line2': shipping_address_obj.line2,
						'postal_code': shipping_address_obj.postcode,
						'state': shipping_address_obj.state,
					},
					'name': f"{shipping_address_obj.first_name} {shipping_address_obj.last_name}",
					'phone': shipping_address_obj.phone_number
				}

				# intent = Facade().payment_intent_update_or_create(
				# 	checkout_session=self.checkout_session,
				# 	customer=self.checkout_session.get_stripe_customer(),
				# 	total=context_data['order_total'],
				# 	shipping=shipping,
				# 	automatic_payment_methods = {"enabled": True},
				# 	# description=self.payment_description(order_number, total, **kwargs),
				# 	# metadata=self.payment_metadata(order_number, total, **kwargs),
				# )
				#
				# self.checkout_session.set_stripe_payment_intent(intent)
				# self.checkout_session.set_stripe_client_secret(intent['client_secret'])

				# data['client_secret'] = payment_intent['client_secret']
				# data['stripe_pkey'] = Facade().pkey

				data['form_structure'] = self.get_form_structure(AdditionalInfoForm, use_help_text=True)


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

				additional_info_obj,created = AdditionalInfoQuestionnaire.objects.update_or_create(
					id=self.checkout_session.get_questionnaire_response('id'),
					defaults={
						'purchase_business_type':form.cleaned_data['purchase_business_type'],
						'business_name':form.cleaned_data['business_name']
						}
				)


				self.checkout_session.set_questionnaire_response(additional_info_obj)
				additional_info_obj.save()
				data['section'] = 'additional_info'
				data['preview_elems'] = {'purchase_business_type': additional_info_obj.purchase_business_type, 'business_name': additional_info_obj.business_name}
				shipping_address = self.get_shipping_address(self.request.basket)
				initial={
					'same_as_shipping':True,
					'first_name': shipping_address.first_name, 'last_name':shipping_address.last_name,
					'line1': shipping_address.line1, 'line2': shipping_address.line2, 'line4': shipping_address.line4,
					'state': shipping_address.state, 'postcode': shipping_address.postcode, 'phone_number': shipping_address.phone_number,
					'country': shipping_address.country
				}

				data['form_structure'] = self.get_form_structure(BillingAddressForm, label_exceptions=['id_same_as_shipping'], initial=initial)
				# data['client_secret'] = self.checkout_session.get_stripe_client_secret()

				## where do we save
				status_code = 200

				# data['client_secret'] = self.checkout_session.get_stripe_payment_intent()['client_secret']
				data['stripe_pkey'] = Facade().pkey

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
		print('\n *** post() billing view ***')
		print(f'\n request.post: {request.POST}')

		data = {}
		status_code = 400

		response = super().post(request, *args, **kwargs)
		context = self.get_context_data(*args, **kwargs)
		total = context['order_total']
		section = 'billing'
		preview_elems = ''

		shipping_address_obj = self.get_shipping_address(self.request.basket)
		shipping = {
			'address': {
				'city': shipping_address_obj.city,
				'country': shipping_address_obj.country,
				'line1': shipping_address_obj.line1,
				'line2': shipping_address_obj.line2,
				'postal_code': shipping_address_obj.postcode,
				'state': shipping_address_obj.state,
			},
			'name': f"{shipping_address_obj.first_name} {shipping_address_obj.last_name}",
			'phone': shipping_address_obj.phone_number
		}

		form = self.form_class(request.POST)

		if self.preview:
			self.form_class = SubmitOrderForm
			form = SubmitOrderForm(request.POST)

			print('form: ', form)
			section = 'place_order'


		payment_method_id = request.POST.get('payment_method_id', None)

		if not form.is_valid():
			print('\n form not valid')
			print('form errors: ', form.errors)
			print('form non_field_errors: ', form.non_field_errors)

		if not request.is_ajax():
			print('\n request not ajax')
			print('form errors: ', form.errors)

		if request.is_ajax() and form.is_valid():
			status_code = 200
			cleaned_data = form.cleaned_data
			data['section'] = section
			if self.preview:
				print('\n handling order placement \n')
				response = self.handle_place_order_submission(request)
				if response.url is "/checkout/thank-you/":
					status_code = 302
					data['redirect'] = True
					data['url'] = response.url
					response = JsonResponse(data)
				else:
					status_code = 400

			elif payment_method_id:

				if cleaned_data['same_as_shipping']:
					self.checkout_session.bill_to_shipping_address()

				intent = Facade().payment_intent_update_or_create(
					self.checkout_session,
					total,
					shipping=shipping,
					payment_method=payment_method_id,
					setup_future_usage='on_session',
					# capture_method='manual',
					# confirm=True,
				)

				preview_elems = {
					'first_name': cleaned_data['first_name'],
					'last_name': cleaned_data['last_name'],
					'phone_number': cleaned_data['phone_number'].raw_input,
					'line1': cleaned_data['line1'],
					'line2': cleaned_data['line2'],
					'line4': cleaned_data['line4'],
					'state': cleaned_data['state'],
					'postcode': cleaned_data['postcode'],
					'country': cleaned_data['country'].printable_name,
				}

				data['status'] = intent['status']
				data['payment_intent_client_secret'] = intent['client_secret']
				print('intent status: ', intent['status'])
				data['form_structure'] = self.get_form_structure(form=SubmitOrderForm, use_labels=True)
				data['preview_elems'] = preview_elems
				response = JsonResponse(data)

		print(f'\nresponse: {response}')
		print(f'\nstatus_code: {status_code}')

		response.status_code = status_code
		return response

	def handle_payment(self, request, order_number, total, *args, **kwargs):
		print('\n handling payment \n')
		"""
		Handle any payment processing and record payment sources and events.
		This method is designed to be overridden within your project.  The
		default is to do nothing as payment is domain-specific.
		This method is responsible for handling payment and recording the
		payment sources (using the add_payment_source method) and payment
		events (using add_payment_event) so they can be
		linked to the order when it is saved later on.
		"""
		context = self.get_context_data(*args, **kwargs)
		total = context['order_total']

		# payment_method_id = request.POST.get('payment_method_id', None)
		payment_intent_id = request.POST.get('payment_intent_id', None) or self.checkout_session.get_stripe_payment_intent()['id']
		payment_method_id  = request.POST.get('payment_method_id', None) or self.checkout_session.get_stripe_payment_method()

		form = self.form_class(request.POST)
		# cleaned_data = form.cleaned_data

		if payment_intent_id:
			setup_future_usage = None
			customer = None
			if hasattr(form, 'cleaned_data') and form.cleaned_data['create_new_account']:
				## create a new user account
				if cleaned_data['remember_payment_info'] and payment_method_id:
					## save the user's payment information and attach it to the account
					customer = Facade().update_or_create_customer(
						checkout_session=self.checkout_session,
						email='',#get the email the user entered earlier
						payment_method=payment_method_id
					)


		intent = Facade().payment_intent_confirm(
			payment_intent_id=payment_intent_id,
			total=total,
			payment_method_id=payment_method_id,
			client_secret=self.checkout_session.get_stripe_client_secret(),
			metadata=self.payment_metadata(order_number, total, **kwargs)
		)

		# description = self.payment_description(intent, order_number, total, **kwargs)


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

	def handle_place_order_submission(self, request):
		print('\n handling place_order_submission \n')
		"""
		Handle a request to place an order.
		This method is normally called after the customer has clicked "place
		order" on the preview page. It's responsible for (re-)validating any
		form information then building the submission dict to pass to the
		`submit` method.
		If forms are submitted on your payment details view, you should
		override this method to ensure they are valid before extracting their
		data into the submission dict and passing it onto `submit`.
		"""
		return self.submit(request, **self.build_submission())

	# noqa (too complex (10))
	def submit(self, request, user, basket, shipping_address, shipping_method, shipping_charge, billing_address, order_total, payment_kwargs=None, order_kwargs=None, surcharges=None):
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

		# Taxes must be known at this point
		assert basket.is_tax_known, (
			"Basket tax must be set before a user can place an order")
		assert shipping_charge.is_tax_known, (
			"Shipping charge tax must be set before a user can place an order")

		# We generate the order number first as this will be used
		# in payment requests (ie before the order model has been
		# created).  We also save it in the session for multi-stage
		# checkouts (e.g. where we redirect to a 3rd party site and place
		# the order on a different request).
		order_number = self.generate_order_number(basket)
		self.checkout_session.set_order_number(order_number)
		logger.info("Order #%s: beginning submission process for basket #%d",
					order_number, basket.id)

		# Freeze the basket so it cannot be manipulated while the customer is
		# completing payment on a 3rd party site.  Also, store a reference to
		# the basket in the session so that we know which basket to thaw if we
		# get an unsuccessful payment response when redirecting to a 3rd party
		# site.
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
		except RedirectRequired as e:
			# Redirect required (e.g. PayPal, 3DS)
			print('\n RedirectRequired \n')

			logger.info("Order #%s: redirecting to %s", order_number, e.url)
			return HttpResponseRedirect(e.url)
		except UnableToTakePayment as e:
			# Something went wrong with payment but in an anticipated way.  Eg
			# their bankcard has expired, wrong card number - that kind of
			# thing. This type of exception is supposed to set a friendly error
			# message that makes sense to the customer.
			print('\n UnableToTakePayment \n')

			msg = str(e)
			logger.warning(
				"Order #%s: unable to take payment (%s) - restoring basket",
				order_number, msg)
			self.restore_frozen_basket()

			# We assume that the details submitted on the payment details view
			# were invalid (e.g. expired bankcard).
			return self.render_payment_details(
				self.request, error=msg, **payment_kwargs)
		except PaymentError as e:
			# A general payment error - Something went wrong which wasn't
			# anticipated.  Eg, the payment gateway is down (it happens), your
			# credentials are wrong - that king of thing.
			# It makes sense to configure the checkout logger to
			# mail admins on an error as this issue warrants some further
			# investigation.
			print('\n PaymentError \n')

			msg = str(e)
			logger.error("Order #%s: payment error (%s)", order_number, msg,
						 exc_info=True)
			self.restore_frozen_basket()
			return self.render_preview(
				self.request, error=error_msg, **payment_kwargs)
		except Exception as e:
			# Unhandled exception - hopefully, you will only ever see this in
			# development...
			logger.exception(
				"Order #%s: unhandled exception while taking payment (%s)",
				order_number, e)
			self.restore_frozen_basket()
			return self.render_preview(
				self.request, error=error_msg, **payment_kwargs)

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

	def payment_description(self, intent, order_number, total, **kwargs):

		return f"payment_intent:{intent['id']} customer: {intent['customer']}, card info: [last4:{intent['charges']['data'][0]['last4']}]"

	def payment_metadata(self, order_number, total, **kwargs):
		return {'order_number': order_number}

	def get_pre_conditions(self, request):
		if self.preview:
			# The preview view needs to ensure payment information has been
			# correctly captured.
			return self.pre_conditions + ['check_payment_data_is_captured']
		return super().get_pre_conditions(request)

	def get_success_url(self):
		return reverse('checkout:thank_you')

class ThankYouView(views.ThankYouView):
	"""
	Displays the 'thank you' page which summarises the order just submitted.
	"""
	template_name = 'dehy/checkout/thank_you.html'
