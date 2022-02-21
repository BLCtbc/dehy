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

	def payment_intent(self, total, confirm=False, currency=settings.STRIPE_CURRENCY, description=None, metadata=None, shipping=None, **kwargs):
		try:

			# Create a PaymentIntent with the order amount and currency
			intent = stripe.PaymentIntent.create(
				confirm=confirm,
				amount=(total.incl_tax * 100).to_integral_value(),
				currency=settings.STRIPE_CURRENCY,
				payment_method_types=["card"],
				confirmation_method='manual'
			)

			return intent
		except Exception as e:
			return json.dumps({
				'error': str(e), 'status_code': 403
			})


	def create_setup_intent(self):
		stripe.SetupIntent.create(
			payment_method_types=["card"],
			usage='on_session'
		)
	def retrieve_payment_intent(self, id, client_secret=None):
		pass

	def confirm_payment_intent(self, id, card, shipping=None, order_number=None, description=None, metadata=None):

		return stripe.PaymentIntent.confirm(
			id,
			payment_method=card, shipping=shipping,
		)

	def generate_payment_response(self, intent):
		if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
			# Tell the client to handle the action
			return json.dumps({
				'requires_action': True,
				'payment_intent_client_secret': intent.client_secret,
		}), 200

		elif intent.status == 'succeeded':
			# The payment didn’t need any additional actions and completed!
			# Handle post-payment fulfillment
			return json.dumps({'success': True}), 200
		else:
			# Invalid status
			return json.dumps({'error': 'Invalid PaymentIntent status'}), 500


	def create_product(self):
		pass

	def retrieve_product(self, id):
		product = stripe.Product.retrieve(id)
		return product

	def session(self, test=True):

		session = stripe.checkout.Session.create(
			line_items=[{
			  'price_data': {
				'currency': 'usd',
				'product_data': {
				  'name': 'Lapel Pin',
				},
				'unit_amount': 500,
			  },
			  'quantity': 1,
			}],
			mode='payment',
			success_url='https://127.0.0.1/success',
			cancel_url='https://127.0.0.1/cancel')

		return session

