from oscar.apps.checkout import utils

class CheckoutSessionData(utils.CheckoutSessionData):
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

	is_stripe_customer_set = is_stripe_customer_field_set
	is_stripe_customer_id_set = is_stripe_customer_field_set