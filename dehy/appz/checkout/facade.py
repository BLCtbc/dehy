from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
import stripe, json
from decimal import Decimal as D

stripe.api_version = '2020-08-27; orders_beta=v2'

class Facade(object):
	def __init__(self):
		print("\n --- Facade instantiated --- \n")
		self.stripe = stripe
		self.stripe.api_key = settings.STRIPE_SECRET_KEY
		self.stripe.pkey = settings.STRIPE_PUBLISHABLE_KEY
		self.stripe.api_version = '2020-08-27; orders_beta=v2'

	@staticmethod
	def get_friendly_decline_message(error):
		return 'The transaction was declined by your bank - please check your bankcard details and try again'

	@staticmethod
	def get_friendly_error_message(error):
		return 'An error occurred when communicating with the payment gateway.'

	def error_handler(self, error):
		print(f'\n ** Facade error: {error}')
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

		elif self.stripe.error.AuthenticationError:
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

	def get_or_create_customer(self, email):
		try:

			customers = stripe.Customer.list(limit=1, email=email)
			if customers.data:
				customer = customers.data[0]
				return customer

			# create the customer
			else:
				customer = stripe.Customer.create(email=email)
				return customer

		except Exception as e:
			return self.error_handler(e)


	def update_or_create_customer(self, checkout_session, payment_method=None, name=None, email=None, description=None, metadata=None, customer=None):

		# see if the customer id exists in the checkout_session first
		try:
			created = False


			if checkout_session.is_stripe_customer_id_set():
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


	def update_and_process_order(self, basket, **order_details):
		try:
			order = self.update_or_create_order(basket, **order_details)
			payment = self.set_order_to_processing(basket, order)
			return payment

		except Exception as e:
			return self.error_handler(e)

	# sets the order's status to processing, returns a payment intent
	# currently done in step 4 of checkout process (billing view)
	def set_order_to_processing(self, basket, order=None):

		try:
			if not order:
				order = self.stripe.Order.retrieve(f"order_{basket.stripe_order_id}")

			if order.status != 'processing':
				order = self.stripe.stripe_object.StripeObject().request('post', f"/v1/orders/{order.id}/submit", {
					'expected_total': order.amount_total,
					'expand': ['payment.payment_intent'],
				})


				payment = order.payment
				basket.payment_intent_client_secret = payment.payment_intent.client_secret
				basket.payment_intent_id = payment.payment_intent.id
				basket.stripe_order_status = order.status
				basket.stripe_order_client_secret = order.client_secret

				basket.save()

				# we add a reference to the order ID so we have a way to look up the order given a payment_intent.success webhook
				self.stripe.PaymentIntent.modify(payment.payment_intent.id, metadata={"order_id": order.id})

				return order

		except Exception as e:
			return self.error_handler(e)

	def update_or_create_order(self, basket, shipping_fields={}, shipping_method={}, discounts=[], billing_fields={}, metadata={}, **kwargs):

		order = ''
		shipping_cost = self.coerce_shipping_cost_object(shipping_method)

		metadata.update({'basket_id': basket.id})
		order_details = kwargs
		order_details.update({'metadata': metadata})

		if shipping_cost:
			metadata.update({
				'shipping_code': shipping_cost['shipping_rate_data']['metadata']['method_code'],
				'shipping_name': shipping_cost['shipping_rate_data']['display_name']
			})

			order_details = {
				'shipping_cost': shipping_cost,
			}


		if basket.stripe_customer_id:
			order_details.update({'customer': basket.stripe_customer_id})

		print('\n ---- shipping_fields: ', shipping_fields)
		if shipping_fields:
			shipping_details = self.coerce_to_address_object(shipping_fields)
			if shipping_details:

				order_details.update({'shipping_details':shipping_details})

		if discounts:
			order_details.update({'discounts':discounts})

		if billing_fields:
			billing_details = self.coerce_to_address_object(billing_fields)
			if billing_details:
				order_details.update({'billing_details':billing_details})

		try:
			### try to update the order
			order = self.update_order(basket, **order_details)

		except:
			print("*** couldn't update order, attempting to create it")
			order = self.create_order(basket, **order_details)

		return order


	def update_order(self, basket, **order_details):
		stripe_order_id = f"order_{basket.stripe_order_id}"
		try:
			order = self.stripe.Order.retrieve(stripe_order_id)

			if order.status == 'processing':
				order = self.stripe.stripe_object.StripeObject().request('post', f'/v1/orders/{stripe_order_id}/reopen', {})

			order = self.stripe.Order.modify(stripe_order_id, line_items=self.get_line_items(basket), **order_details)

			print('order updated: ', order)
			basket.stripe_order_status = order.status
			basket.save()

			return order

		except Exception as e:
			return self.error_handler(e)


	def create_order(self, basket, **order_details):

		order_details.update({
			"currency": "usd",
			"payment":{
				"settings": {
				  "payment_method_types": ["card"],
				}
			},
			"expand":["line_items"],
			"automatic_tax": {
				"enabled":True
			}
		})

		try:
			order = self.stripe.Order.create(line_items=self.get_line_items(basket), **order_details)
			basket.stripe_order_id = str(order.id).replace("order_", "")
			basket.stripe_order_status = order.status
			basket.save()

			print('order created: ', order)
			return order

		except Exception as e:
			return self.error_handler(e)

	def get_line_items(self, basket):
		line_items = []
		for line in basket.lines.all():
			line_items.append({
				"product": line.product.upc,
				"quantity": line.quantity
			})
		return line_items

	## expects a 'cost' in decimal form, and a 'code' or 'name'
	def coerce_shipping_cost_object(self, shipping_method_data):
		shipping_cost = {}
		amount = shipping_method_data['cost'] if shipping_method_data.get('cost', None) else shipping_method_data.get('amount', None)
		if amount:

			amount = str((D(amount)*100).to_integral())

		display_name = shipping_method_data.get('name', None)
		method_code = shipping_method_data.get('code', None)

		if amount and display_name and method_code:

			shipping_cost = {
				'shipping_rate_data': {
					'display_name': display_name,
					'type':'fixed_amount',
					'fixed_amount': {
						'amount': amount,
						'currency': 'usd'
					},
					'tax_behavior': 'exclusive',
					'metadata': {
						'method_code':method_code,
					}
				}
			}

			if shipping_method_data.get('name', None):
				shipping_cost['shipping_rate_data']['metadata'].update({'name':shipping_method_data.get('name')})

		return shipping_cost

	## turns shipping/billing address fields into stripe's expected form
	def coerce_to_address_object(self, address_fields):
		address_details = {}
		name = address_fields.get('first_name', 'anon')
		name = f"{name} {address_fields['last_name']}" if address_fields.get('last_name', None) else name
		country = address_fields['country'] if address_fields.get('country', None) else address_fields.get('country_id')

		if address_fields.get('postcode', None) and country and name:

			address_details = {
				'address': {
					'postal_code':address_fields['postcode'],
					'country':country
				},
				'name': name
			}

			if address_fields.get('state', None):
				address_details['address']['state'] = address_fields.get('state')

			if address_fields.get('line1', None):
				address_details['address']['line1'] = address_fields.get('line1')

			if address_fields.get('line2', None):
				address_details['address']['line2'] = address_fields.get('line2')

			if address_fields.get('line3', None):
				address_details['address']['line3'] = address_fields.get('line3')

			city = address_fields['city'] if address_fields.get('city', None) else address_fields.get('line4', None)
			if city:
				address_details['address']['city'] = city

			phone = address_fields.get('phone_number', None)
			if phone:
				address_details['phone'] = phone

			email = address_fields.get('email', None)
			if email:
				address_details['email'] = email

		return address_details


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
				intent = self.stripe.PaymentIntent.retrieve(client_secret)
				if intent['amount'] != (total.incl_tax * 100).to_integral_value():
					print('\n updating the paymentintent ')
					intent = self.stripe.PaymentIntent.modify(
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

				intent = self.stripe.PaymentIntent.create(
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
			return self.stripe.Charge.create(
				amount=(total.incl_tax * 100).to_integral_value(),
				shipping=shipping,
				currency=currency,
				card=card,
				description=description,
				metadata=(metadata or {'order_number': order_number}),
				**kwargs).id

		except self.stripe.error.CardError as e:
			raise UnableToTakePayment(self.get_friendly_decline_message(e))
		except self.stripe.error.StripeError as e:
			raise InvalidGatewayRequestError(self.get_friendly_error_message(e))




def upload_catalog():
	from django.db.models import Count, Q
	from decimal import Decimal as D

	stripe.api_key = settings.STRIPE_SECRET_KEY
	stripe.pkey = settings.STRIPE_PUBLISHABLE_KEY

	TWOPLACES = Decimal(10)**-2
	product_list = Product.objects.filter(Q(product_class__name='Merchandise') | ~Q(parent=None))
	for product in product_list:
		base_url = ""
		images = product.parent.images.all() if product.parent else product.images.all()
		image_urls = [f"https://www.dehygarnish.com{image.original.url}" for image in images]
		# see https://stripe.com/docs/tax/tax-codes for a list of tax-codes
		tax_code = 'txcd_99999999' #Food and food ingredients for home consumption.
		description = product.description
		name = f"{product.title}"
		if 'wholesale' in product.title.lower():
			tax_code = 'txcd_40040000'
		if product.parent and product.parent.product_class and product.parent.product_class.name != 'Merchandise':
			name = f"{product.parent.title}: {product.title}"
			description = product.parent.description
		try:
			# product = stripe.Product.retrieve(id=product.upc)
			product = stripe.Product.modify(
				product.upc,
				description=description,
				tax_code=tax_code
			)
			print('updated product')
			continue
			product = stripe.Product.modify(
				product.upc,
				price_data={
					"currency": "usd",
					"unit_amount": str((product.stockrecords.all()[0].price*100).to_integral()),
					"tax_behavior": "exclusive",
				},
				description=product.parent.description,
				images=image_urls, #list of image urls
				package_dimensions={
					"length":product.length, # inches
					"width":product.width,
					"height":product.height,
					"weight":D.max(D(product.weight*16).quantize(TWOPLACES), D(0.01)), # ounces
				},
				sku=product.upc,
				shippable=True,
				tax_code=tax_code
			)
		except:
			product = stripe.Product.create(
				name=name,
				id=product.upc,
				default_price_data={
					"currency": "usd",
					"unit_amount": str((product.stockrecords.all()[0].price*100).to_integral()),
					"tax_behavior": "exclusive",
				},
				description=description,
				images=image_urls, #list of image urls
				package_dimensions={
					"length":product.length, # inches
					"width":product.width,
					"height":product.height,
					"weight":D.max(D(product.weight*16).quantize(TWOPLACES), D(0.01)), # ounces
				},
				sku=product.upc,
				shippable=True,
				tax_code=tax_code
			)
