from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from django.http import JsonResponse
import stripe, json



class Facade(object):
	def __init__(self):
		stripe.api_key = settings.STRIPE_SECRET_KEY

	@staticmethod
	def get_friendly_decline_message(error):
		return 'The transaction was declined by your bank - please check your bankcard details and try again'

	@staticmethod
	def get_friendly_error_message(error):
		return 'An error occurred when communicating with the payment gateway.'


	def charge(self,
		order_number,
		total,
		card,
		currency=settings.STRIPE_CURRENCY,
		description=None,
		metadata=None,
		shipping=None,
		**kwargs):
		try:
			return stripe.Charge.create(
				amount=(total.incl_tax * 100).to_integral_value(),
				shipping=shipping,
				currency=currency,
				card=card,
				description=description,
				metadata=(metadata or {'order_number': order_number}),
				**kwargs).id

		except stripe.error.CardError as e:
			raise UnableToTakePayment(self.get_friendly_decline_message(e))
		except stripe.error.StripeError as e:
			raise InvalidGatewayRequestError(self.get_friendly_error_message(e))

	def create_payment_intent(self, total, currency=settings.STRIPE_CURRENCY, description=None, metadata=None, shipping=None, **kwargs):
		try:
			# Create a PaymentIntent with the order amount and currency
			intent = stripe.PaymentIntent.create(
				amount=(total.incl_tax * 100).to_integral_value(),
				currency=settings.STRIPE_CURRENCY,
				automatic_payment_methods={
					'enabled': True,
				},
			)
			# return json.dumps({
			# 	'clientSecret': intent['client_secret']
			# })
			return intent
		except Exception as e:
			return json.dumps({
				'error': str(e), 'status_code': 403
			})
			# response = JsonResponse(data={'error':str(e)})
			# response.status_code = 403
			# return response

		# old
		# try:
		# 	return stripe.Charge.create(
		# 		amount=(total.incl_tax * 100).to_integral_value(),
		# 		shipping=shipping,
		# 		currency=currency,
		# 		card=card,
		# 		description=description,
		# 		metadata=(metadata or {'order_number': order_number}),
		# 		**kwargs).id
		#
		# except stripe.error.CardError as e:
		# 	raise UnableToTakePayment(self.get_friendly_decline_message(e))
		# except stripe.error.StripeError as e:
		# 	raise InvalidGatewayRequestError(self.get_friendly_error_message(e))