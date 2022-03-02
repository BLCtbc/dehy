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

	def payment_intent_update_or_create(self, checkout_session, total, customer=None, email=None, name=None, client_secret=None,
			currency=settings.STRIPE_CURRENCY, description=None, metadata=None,
			shipping=None, customer_required=True, **kwargs):

		try:
			# Create or update a PaymentIntent with the order amount
			if not customer:
				print('\n creating new customer \n')
				customer = self.get_or_create_customer(checkout_session, email=email, description=description, metadata=metadata)
			intent = ''
			print('\n client_secret: ', client_secret)
			if client_secret:
				intent = stripe.PaymentIntent.retrieve(client_secret)

				if intent['amount'] != (total.incl_tax * 100).to_integral_value():

					intent = stripe.PaymentIntent.modify(
						client_secret,
						# customer=customer['id'],
						amount=(total.incl_tax * 100).to_integral_value(),
						currency=currency,
						shipping=shipping,
						description=description,
						metadata=metadata,
					)

			else:
				intent = stripe.PaymentIntent.create(
					customer=customer['id'],
					setup_future_usage='on_session',
					amount=(total.incl_tax * 100).to_integral_value(),
					currency=currency,
					shipping=shipping,
					automatic_payment_methods={
	    				'enabled': True,
	  				},
					description=description,
					metadata=metadata,
				)

			checkout_session.set_stripe_payment_intent(intent)

			return intent

		except Exception as e:
			return self.error_handler(e)

		# except Exception as e:
		# 	return json.dumps({
		# 		'error': str(e), 'status_code': 403
		# 	})

	def get_or_create_customer(self, checkout_session, name=None, email=None, description=None, metadata=None):

		# see if the customer id exists in the checkout_session first
		customer = None
		try:
			created = False
			if checkout_session.is_stripe_customer_id_set():
				print('\n retrieving customer: \n')
				customer = stripe.Customer.retrieve(
					id=checkout_session.get_stripe_customer_id(),
					email=email,
					name=name,
					description=description,
					metadata=metadata,
				)
			else:
				customer = stripe.Customer.create(
					email=email,
					name=name,
					description=description,
					metadata=metadata
				)
				created = True

			if created:
				checkout_session.set_stripe_customer(customer)

			return customer

		except Exception as e:
			return self.error_handler(e)



