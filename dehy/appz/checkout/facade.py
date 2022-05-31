from django.conf import settings
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
import stripe, json
from decimal import Decimal as D
from oscar.core.loading import get_model
from phonenumber_field.phonenumber import PhoneNumber

Country = get_model('address', 'Country')

# stripe.api_version = '2020-08-27; orders_beta=v2'
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.pkey = settings.STRIPE_PUBLISHABLE_KEY
stripe.api_version = '2020-08-27; orders_beta=v3'

class Facade(object):

	def __init__(self):
		self.stripe = stripe
		self.STRIPE_ORDER_SUBMITTED_SIGNING_SECRET = settings.STRIPE_ORDER_SUBMITTED_SIGNING_SECRET
		self.STRIPE_CLI_WEBHOOK_SIGNING_SECRET = 'whsec_63c2ac70680ad9eb9ceddd981cb1be311fbd0ab114767d63c69c28f0374d8b42'

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
		amount = shipping_method_data.get('amount', None) or shipping_method_data.get('cost', None)
		if amount != None:
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

		if isinstance(country, Country):
			country = country.iso_3166_1_a2

		if address_fields.get('postcode', None) and country and name:

			address_details = {
				'address': {
					'postal_code':address_fields['postcode'],
					'country': country
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
				if isinstance(address_details['phone'], PhoneNumber):
					address_details['phone'] = address_details['phone'].as_international

			email = address_fields.get('email', None)
			if email:
				address_details['email'] = email

		return address_details


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

	def update_or_create_order(self, basket, customer=None, shipping_fields={}, shipping_method={}, discounts=[], billing_fields={}, metadata={}, **kwargs):

		if basket.status != 'Open':
			return False

		order = ''
		metadata.update({'basket_id': basket.id})
		order_details = kwargs
		order_details.update({'metadata': metadata})

		shipping_cost = self.coerce_shipping_cost_object(shipping_method)
		if shipping_cost:
			if shipping_cost['shipping_rate_data']['metadata'].get('method_code', None):
				metadata.update({
					'shipping_code': shipping_cost['shipping_rate_data']['metadata']['method_code']
				})

			if shipping_cost['shipping_rate_data'].get('display_name', None):
				metadata.update({
					'shipping_name': shipping_cost['shipping_rate_data']['display_name']
				})


			order_details.update({'shipping_cost': shipping_cost, 'metadata': metadata})



		if customer:
			order_details.update({'customer': customer})

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
			# what if
			# basket is already tied to an order, update it
			if basket.stripe_order_id:

				stripe_order_id = f"order_{basket.stripe_order_id}"
				order = self.stripe.Order.modify(stripe_order_id, line_items=self.get_line_items(basket), **order_details)

			# basket not tied to an order, create the order
			else:
				order = self.create_order(basket, **order_details)

		except Exception as e:
			return self.error_handler(e)

		return order

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
				"enabled": True
			}
		})

		try:
			order = self.stripe.Order.create(line_items=self.get_line_items(basket), **order_details)
			basket.stripe_order_id = str(order.id).replace("order_", "")
			basket.stripe_order_status = order.status
			basket.save()

			return order

		except Exception as e:
			return self.error_handler(e)

facade = Facade()

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
