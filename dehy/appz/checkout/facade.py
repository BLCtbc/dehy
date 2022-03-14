from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from django.http import JsonResponse
import stripe, json


class Facade(object):
	def __init__(self):
		stripe.api_key = settings.STRIPE_SECRET_KEY
		stripe.pkey = self.pkey = settings.STRIPE_PUBLISHABLE_KEY

	@staticmethod
	def get_friendly_decline_message(error):
		return 'The transaction was declined by your bank - please check your bankcard details and try again'

	@staticmethod
	def get_friendly_error_message(error):
		return 'An error occurred when communicating with the payment gateway.'

	def error_handler(self, error):
		print('\n ** error handler ** \n')
		print(f'\n ** error: {error}')

		message = "Something else happened, completely unrelated to Stripe"
		print('Code is: %s' % error.code)
		# param is '' in this case
		print('Param is: %s' % error.param)
		print('Message is: %s' % error.user_message)
		if error.CardError:
			message = "The transaction was declined - please check your card details and try again"

		elif error.RateLimitError:
			message = "Too many requests made to the API too quickly"

		elif error.InvalidRequestError:
		# Invalid parameters were supplied to Stripe's API
			message = "Invalid parameters were supplied to Stripe's API"

		elif stripe.error.AuthenticationError:
		# Authentication with Stripe's API failed
		# (maybe you changed API keys recently)
			message = "Authentication with Stripe's API failed (maybe you changed API keys recently)"

		elif error.APIConnectionError:
			# Network communication with Stripe failed
			message = "Network communication with Stripe failed"

		elif error.StripeError:
			# Display a very generic error to the user, and maybe send
			# yourself an email
			message = 'An error occurred when communicating with the payment gateway.'

		return message



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

	def payment_intent_update_or_create(self, checkout_session, total, payment_method=None, capture_method='automatic',
			confirm=False, confirmation_method='automatic', customer=None, email=None, name=None,
			client_secret=None, currency=settings.STRIPE_CURRENCY, description=None, metadata=None,
			shipping=None, setup_future_usage='off_session', **kwargs):

		try:
			# Create or update a PaymentIntent with the order amount
			if not customer:
				print('\n getting customer \n')
				customer = self.update_or_create_customer(checkout_session, payment_method=payment_method, email=email, description=description, metadata=metadata)

			intent = ''

			if client_secret:
				print('\n retrieving the paymentintent using client_secret: ', client_secret)
				intent = stripe.PaymentIntent.retrieve(client_secret)
				if intent['amount'] != (total.incl_tax * 100).to_integral_value():
					print('\n updating the paymentintent ')
					intent = stripe.PaymentIntent.modify(
						client_secret,
						payment_method=payment_method,
						confirmation_method=confirmation_method,
						customer=customer['id'],
						amount=(total.incl_tax * 100).to_integral_value(),
						currency=currency,
						shipping=shipping,
						description=description,
						metadata=metadata,
						confirm=confirm,
						setup_future_usage=setup_future_usage

					)



			else:
				print('\n creating paymentintent ')

				intent = stripe.PaymentIntent.create(
					customer=customer,
					payment_method=payment_method,
					confirmation_method=confirmation_method,
					amount=(total.incl_tax * 100).to_integral_value(),
					capture_method=capture_method,
					currency=currency,
					shipping=shipping,
					description=description,
					metadata=metadata,
					confirm=confirm,
					setup_future_usage=setup_future_usage
				)

			checkout_session.set_stripe_payment_intent(intent)
			checkout_session.set_stripe_client_secret(intent.client_secret)

			print('\n intent: ', intent)
			return intent

		except Exception as e:
			return self.error_handler(e)

	def payment_intent_confirm(self, payment_intent_id, payment_method_id, total, client_secret=None,
		setup_future_usage='off_session', shipping=None, **kwargs):

		print('\n *** confirming payment intent')
		try:
			# print('retrieving payment intent')
			# intent = stripe.PaymentIntent.retrieve(
			# 	"pi_3KTcllLpSVHc8H4y0aWYEIeO",
			# )
			print('payment_intent_id: ', payment_intent_id)
			print('payment_method_id: ', payment_method_id)
			print('client_secret: ', client_secret)

			intent = stripe.PaymentIntent.confirm(
				payment_intent_id,
				# client_secret=client_secret,
				# payment_method=payment_method_id,
				# setup_future_usage=setup_future_usage,
				# payment_method=payment_method_id
			)

			print(f'\n *** payment intent confirmed: {intent}')

			return intent

		except Exception as e:
			return self.error_handler(e)

	def payment_intent_capture(self, payment_intent_id, **kwargs):

		print('\n *** capturing payment intent')
		try:

			intent = stripe.PaymentIntent.capture(
				payment_intent_id,
			)

			print(f'\n *** payment intent captured: {intent}')

			return intent

		except Exception as e:
			return self.error_handler(e)

	def generate_response(self, intent):
		# Note that if your API version is before 2019-02-11, 'requires_action'
		# appears as 'requires_source_action'.
		if intent.status == 'requires_action' and intent.next_action.type == 'use_stripe_sdk':
			# Tell the client to handle the action
			print('requires_action')
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

	def update_or_create_customer(self, checkout_session, payment_method=None, name=None, email=None, description=None, metadata=None, customer=None):

		# see if the customer id exists in the checkout_session first
		try:
			created = False


			if checkout_session.is_stripe_customer_id_set():

				print('\n retrieving customer \n')
				customer = stripe.Customer.retrieve(
					id=checkout_session.get_stripe_customer_id(),
					payment_method=payment_method,
					email=email,
					name=name,
					description=description,
					metadata=metadata,
				)
			else:
				print('\n creating new customer \n')
				customer = stripe.Customer.create(
					email=email,
					payment_method=payment_method,
					name=name,
					description=description,
					metadata=metadata
				)


			if payment_method:
				stripe.PaymentMethod.attach(
					payment_method,
					customer=customer['id'],
				)

			checkout_session.set_stripe_customer(customer)

			return customer

		except Exception as e:
			return self.error_handler(e)



