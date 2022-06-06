from oscar.apps.checkout import utils
from phonenumber_field.phonenumber import PhoneNumber
from oscar.core.loading import get_class, get_model

BaseFedex = get_class('shipping.methods', 'BaseFedex')
Country = get_model('address', 'Country')
ConditionalOffer = get_model('offer', 'ConditionalOffer')
OfferDiscount = get_class('shipping.methods', 'OfferDiscount')
TaxInclusiveOfferDiscount = get_class('shipping.methods', 'TaxInclusiveOfferDiscount')

class CheckoutSessionData(utils.CheckoutSessionData):
	def _set(self, namespace, key, value):
		"""
		Set a namespaced value
		"""
		self._check_namespace(namespace)
		self.request.session[self.SESSION_KEY][namespace][key] = value
		self.request.session.modified = True

	def ship_to_new_address(self, address_fields):
		"""
		Use a manually entered address as the shipping address
		"""

		self._unset('shipping', 'new_address_fields')
		phone_number = address_fields.get('phone_number')
		if phone_number and isinstance(phone_number, PhoneNumber):
			# Phone number is stored as a PhoneNumber instance. As we store
			# strings in the session, we need to serialize it.
			address_fields = address_fields.copy()
			address_fields['phone_number'] = phone_number.as_international

		country = address_fields.get('country', None)

		if country and isinstance(country, Country):

			address_fields = address_fields.copy()
			address_fields['country'] = address_fields['country'].iso_3166_1_a2

		self._set('shipping', 'new_address_fields', address_fields)

	def bill_to_new_address(self, address_fields):
		"""
		Store address fields for a billing address.
		"""

		self._unset('billing', 'new_address_fields')

		phone_number = address_fields.get('phone_number')
		if phone_number and isinstance(phone_number, PhoneNumber):
			# Phone number is stored as a PhoneNumber instance. As we store
			# strings in the session, we need to serialize it.
			address_fields = address_fields.copy()
			address_fields['phone_number'] = phone_number.as_international

		country = address_fields.get('country', None)
		if country and isinstance(country, Country):

			address_fields = address_fields.copy()
			address_fields['country'] = address_fields['country'].iso_3166_1_a2

		self._set('billing', 'new_address_fields', address_fields)

	def set_questionnaire_response(self, additional_info):
		self._set('questionnaire', 'purchase_business_type', additional_info.purchase_business_type)
		self._set('questionnaire', 'business_name', additional_info.business_name)
		self._set('questionnaire', 'additional_info_id', additional_info.id)

	def get_questionnaire_response(self, field='id'):
		return self._get('questionnaire', field)

	def is_questionnaire_response_set(self, basket):
		"""
		Test if additional info object id is stored in the session
		"""
		return self.get_questionnaire_response() is not None

	def set_stripe_customer(self, customer):
		self._set('stripe', 'customer', customer)

	def get_stripe_customer(self):
		return self._get('stripe', 'customer')

	def get_stripe_customer_id(self, field='id'):
		return getattr(self._get('stripe', 'customer'), 'id', None)

	def is_stripe_customer_field_set(self, field='id'):
		return self.get_stripe_customer_id() is not None

	def set_stripe_payment_intent(self, payment_intent):
		self._set('stripe', 'payment_intent', payment_intent)

	def get_stripe_payment_intent(self):
		return self._get('stripe', 'payment_intent')

	def is_stripe_payment_intent_set(self):
		return self.get_stripe_payment_intent() is not None

	def set_stripe_payment_method(self, payment_method):
		self._set('stripe', 'payment_method', payment_method)

	def get_stripe_payment_method(self):
		return self._get('stripe', 'payment_method')

	def is_stripe_payment_method_set(self):
		return self.get_stripe_payment_method() is not None

	def set_stripe_client_secret(self, client_secret):
		self._set('stripe', 'client_secret', client_secret)

	def get_stripe_client_secret(self):
		return self._get('stripe', 'client_secret')

	def is_stripe_client_secret_set(self):
		return self.get_stripe_client_secret() is not None

	def get_stored_shipping_methods(self):
		free_ground_shipping = ConditionalOffer.objects.get(slug='free-ground-shipping')

		self._check_namespace('shipping_methods')
		shipping_methods = []

		for method_code, val in self.request.session[self.SESSION_KEY]['shipping_methods'].items():
			method = BaseFedex(code=method_code, name=val['name'], charge_excl_tax=val['cost'], charge_incl_tax=val['cost'])
			if val.get('discount'):
				method.charge_excl_tax = val.get('discount')
				method.charge_incl_tax = val.get('discount')

				method = TaxInclusiveOfferDiscount(method, free_ground_shipping)

			shipping_methods.append(method)

		return shipping_methods

	def store_shipping_methods(self, basket, methods):
		self._flush_namespace('shipping_methods')
		for method in methods:
			method_data = {'name': method.name, 'cost':str(method.calculate(basket).excl_tax)}
			if hasattr(method, 'discount') and method.discount(basket) > 0:
				method_data['discount'] = str(method.discount(basket))
				method_data['cost'] = str(method.discount(basket))

			self.request.session[self.SESSION_KEY]['shipping_methods'][method.code] = method_data


	def new_shipping_address_fields(self):
		"""
		Return shipping address fields
		"""
		return self._get('shipping', 'new_address_fields')

	def bill_to_shipping_address(self):
		"""
		Record fact that the billing address is to be the same as
		the shipping address.
		"""
		self._flush_namespace('billing')
		self._set('billing', 'billing_address_same_as_shipping', True)

	# get_shipping_address = new_shipping_address_fields
	is_stripe_customer_set = is_stripe_customer_field_set
	is_stripe_customer_id_set = is_stripe_customer_field_set
