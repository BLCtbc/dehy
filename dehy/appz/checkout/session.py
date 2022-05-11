from oscar.apps.checkout import exceptions, session
from oscar.core.loading import get_class, get_model
from django import http
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from bs4 import BeautifulSoup
# from dehy.appz.shipping.methods import BaseFedex
from oscar.core import prices
import json
from decimal import Decimal as D

from dehy.appz.checkout import utils, tax
from . import FormStructure

CheckoutSessionData = utils.CheckoutSessionData
Repository = get_class('shipping.repository', 'Repository')
BaseFedex = get_class('shipping.methods', 'BaseFedex')
SurchargeApplicator = get_class("checkout.applicator", "SurchargeApplicator")
ShippingAddress = get_model('order', 'ShippingAddress')
Country = get_model('address', 'Country')
UserAddress = get_model('address', 'UserAddress')

class CheckoutSessionMixin(session.CheckoutSessionMixin):
	def check_a_valid_shipping_method_is_captured(self):

		# Check that shipping method has been set
		if not self.checkout_session.is_shipping_method_set(self.request.basket):
			pass

			# raise exceptions.FailedPreCondition(
			# 	url=reverse('checkout:shipping'),
			# 	message=_("Please choose a shipping method")
			# )

		# Check that a *valid* shipping method has been set
		shipping_address = self.get_shipping_address(
			basket=self.request.basket)
		shipping_method = self.get_shipping_method(
			basket=self.request.basket,
			shipping_address=shipping_address)
		if not shipping_method:
			pass
			# raise exceptions.FailedPreCondition(
			# 	url=reverse('checkout:shipping'),
			# 	message=_("Your previously chosen shipping method is "
			# 			  "no longer valid.  Please choose another one")
			# )

	def check_shipping_data_is_captured(self, request):

		if not request.basket.is_shipping_required():
			# Even without shipping being required, we still need to check that
			# a shipping method code has been set.
			if not self.checkout_session.is_shipping_method_set(self.request.basket):
				pass
				# raise exceptions.FailedPreCondition(
				# 	url=reverse('checkout:shipping'),
				# )
			return

		self.check_a_valid_shipping_address_is_captured()
		self.check_a_valid_shipping_method_is_captured()

	def check_a_valid_shipping_address_is_captured(self):

		# Check that shipping address has been completed
		if not self.checkout_session.is_shipping_address_set():

			pass
			# raise exceptions.FailedPreCondition(
			# 	url=reverse('checkout:shipping'),
			# 	message=_("Please choose a shipping address")
			# )

		# Check that the previously chosen shipping address is still valid
		shipping_address = self.get_shipping_address(
			basket=self.request.basket)
		if not shipping_address:
			pass
			# raise exceptions.FailedPreCondition(
			# 	url=reverse('checkout:shipping'),
			# 	message=_("Your previously chosen shipping address is "
			# 			  "no longer valid.  Please choose another one")
			# )


	def get_shipping_address(self, basket):

		if not basket.is_shipping_required():
			return None

		addr_data = self.checkout_session.new_shipping_address_fields()

		if addr_data:

			# Load address data into a blank shipping address model
			if addr_data.get('country', None) and not isinstance(addr_data['country'], Country):
				addr_data['country'] = Country.objects.get(iso_3166_1_a2=addr_data['country'])

			return ShippingAddress(**addr_data)

		addr_id = self.checkout_session.shipping_user_address_id()
		if addr_id:
			try:
				address = UserAddress._default_manager.get(pk=addr_id)
			except UserAddress.DoesNotExist:
				# An address was selected but now it has disappeared.  This can
				# happen if the customer flushes their address book midway
				# through checkout.  No idea why they would do this but it can
				# happen.  Checkouts are highly vulnerable to race conditions
				# like this.
				return None
			else:
				# Copy user address data into a blank shipping address instance
				shipping_addr = ShippingAddress()
				address.populate_alternative_model(shipping_addr)
				return shipping_addr

	def get_shipping_method(self, basket, shipping_address=None, **kwargs):
		"""
		Return the selected shipping method instance from this checkout session
		The shipping address is passed as we need to check that the method
		stored in the session is still valid for the shipping address.
		"""

		code = self.checkout_session.shipping_method_code(basket)


		# methods,status_code = Repository().get_shipping_methods(
		# 	basket=basket, user=self.request.user,
		# 	shipping_addr=shipping_address, request=self.request)

		methods = self.checkout_session.get_stored_shipping_methods()

		for method in methods:
			if method.code == code:
				return method

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['stripe_pkey'] = settings.STRIPE_PUBLISHABLE_KEY
		# ctx['basket'] = self.request.basket
		return ctx

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

	def check_user_email_is_captured(self, request):
		print('\n check_user_email_is_captured')
		if not request.user.is_authenticated and not self.checkout_session.get_guest_email():
			print('\n no email address captured')

			raise exceptions.FailedPreCondition(
				url=reverse('checkout:checkout'),
				message=_(
					"Please either sign in or enter your email address")
			)

	def check_stripe_user_id_is_captured(self, request):
		if not self.checkout_session.get_stripe_customer_id():
			raise exceptions.FailedPreCondition(
				url=reverse('checkout:checkout'),
				message=_("Please either sign in or enter your email address"),
			)

	def skip_unless_payment_is_required(self, request):
		# Check to see if payment is actually required for this order.
		shipping_address = self.get_shipping_address(request.basket)
		shipping_method = self.get_shipping_method(
			request.basket, shipping_address)
		if shipping_method:
			shipping_charge = shipping_method.calculate(request.basket)
		else:
			# It's unusual to get here as a shipping method should be set by
			# the time this skip-condition is called. In the absence of any
			# other evidence, we assume the shipping charge is zero.
			shipping_charge = prices.Price(
				currency=request.basket.currency, excl_tax=D('0.00'),
				tax=D('0.00')
			)

		surcharges = SurchargeApplicator(request).get_applicable_surcharges(
			basket=request.basket, shipping_charge=shipping_charge
		)
		total = self.get_order_totals(request.basket, shipping_charge, surcharges)
		if total.excl_tax == D('0.00'):
			print("total.excl_tax: ", total.excl_tax)

			raise exceptions.PassedSkipCondition(
				url=reverse('checkout:place_order')
			)

	def build_submission(self, **kwargs):
		"""
		Return a dict of data that contains everything required for an order
		submission.  This includes payment details (if any).
		This can be the right place to perform tax lookups and apply them to
		the basket.
		"""
		# Pop the basket if there is one, because we pass it as a positional
		# argument to methods below
		basket = kwargs.pop('basket', self.request.basket)
		shipping_address = self.get_shipping_address(basket)
		shipping_method = self.get_shipping_method(
			basket, shipping_address)
		billing_address = self.get_billing_address(shipping_address)
		submission = {
			'user': self.request.user,
			'basket': basket,
			'shipping_address': shipping_address,
			'shipping_method': shipping_method,
			'billing_address': billing_address,
			'order_kwargs': {},
			'payment_kwargs': {}
		}

		if not shipping_method:
			total = shipping_charge = surcharges = None
		else:
			shipping_charge = shipping_method.calculate(basket)
			surcharges = SurchargeApplicator(self.request, submission).get_applicable_surcharges(
				self.request.basket, shipping_charge=shipping_charge
			)
			total = self.get_order_totals(
				basket, shipping_charge=shipping_charge, surcharges=surcharges, **kwargs)

		submission["shipping_charge"] = shipping_charge
		submission["order_total"] = total
		submission['surcharges'] = surcharges

		# If there is a billing address, add it to the payment kwargs as calls
		# to payment gateways generally require the billing address. Note, that
		# it normally makes sense to pass the form instance that captures the
		# billing address information. That way, if payment fails, you can
		# render bound forms in the template to make re-submission easier.
		if billing_address:
			submission['payment_kwargs']['billing_address'] = billing_address

		# Allow overrides to be passed in
		submission.update(kwargs)

		# Set guest email after overrides as we need to update the order_kwargs
		# entry.
		user = submission['user']
		if (not user.is_authenticated
				and 'guest_email' not in submission['order_kwargs']):
			email = self.checkout_session.get_guest_email()
			submission['order_kwargs']['guest_email'] = email


		return submission

	def get_form_structure(self, form, use_placeholders=False, use_labels=True, use_help_text=True,
		label_exceptions=[], initial={}, submit_text='Continue'):
		form = form(initial) if form else self.form_class(initial)
		outter_tags = ['select', 'input', 'fieldset']
		inner_tags = ['input', 'option']
		if use_labels or label_exceptions:
			outter_tags+=['label']
			inner_tags+=['label']

		if use_help_text:
			outter_tags+=[('span', 'helptext')]
			inner_tags+=[('span', 'helptext')]

		form_structure = [{'tag':'div', 'classes':'form-container', 'elems': []}]
		soup = BeautifulSoup(form.as_table(), 'html.parser')

		for row in soup.find_all('tr'):
			row_element = {'tag': 'div', 'classes':'row', 'attrs': row.attrs, 'elems':[]}
			if not row_element['attrs']: row_element.pop('attrs')

			field_element = {'tag': 'div', 'classes':'form-floating input-group col', 'elems':[]}

			for elem in row.find_all(outter_tags):
				elem_dict = {'tag': elem.name, 'attrs': elem.attrs, 'elems':[]}
				if 'class' not in elem_dict['attrs'].keys():
					elem_dict['attrs']['class'] = []

				if elem.name == 'label':
					for_attr = elem.attrs['for']
					if use_labels or (use_labels and for_attr in label_exceptions):
						elem_dict['text'] = elem.text
					else:
						continue

				else:
					elem_dict['attrs']['class'] += ['form-control']

					if 'name' in elem.attrs.keys():
						elem_dict['attrs']['placeholder'] = elem.attrs['name']

					if 'type' in elem.attrs.keys():
						elem_dict['attrs']['autofill'] = elem.attrs['type']

				if elem.has_attr('required'):
					elem_dict['attrs']['class'] += ['required']

				if use_help_text and elem.name=='span' and 'helptext' in elem.attrs['class']:
					elem_dict.update({'text':elem.text})
					elem_dict['attrs']['class'] = ['helptext']

				if elem_dict['attrs']['class']:
					elem_dict['attrs']['class'] = " ".join(elem_dict['attrs']['class'])
				else:
					elem_dict['attrs'].pop('class')

				child_elems = []

				for child in elem.findChildren(inner_tags):
					child_elems.append({'tag':child.name, 'text': child.text, 'attrs':child.attrs})
					if child.has_attr('required'):
						child_elems[-1]['classes'] = 'required'

				if child_elems:
					elem_dict['elems'] = child_elems

				if not elem_dict['elems']: elem_dict.pop('elems')

				field_element['elems'].append(elem_dict)

			row_element['elems'].append(field_element)
			form_structure[-1]['elems'].append(row_element)


		form_structure.append(FormStructure().get_submit_button_error_container())
		# print(f"\n form structure for {self.form_class} : {json.dumps(form_structure)}")

		return form_structure

