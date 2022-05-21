from oscar.apps.shipping import repository
from dehy.appz.shipping.methods import BaseFedex, FreeShipping
from dehy.appz.generic.models import FedexAuthToken as FedexAuthTokenModel

import base64, datetime, json, requests, xmltodict
from oscar.core.loading import get_class, get_model
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

import asyncio, logging
from asgiref.sync import sync_to_async
from decimal import Decimal as D
TWOPLACES = D(10) ** -2

Order = get_model('order', 'Order')
Basket = get_model('basket', 'Basket')

logger = logging.getLogger(__name__)
# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods

# class Repository(repository.Repository):
# 	methods = (shipping_methods.Standard(), shipping_methods.Express())

class Repository(repository.Repository):
	def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
		methods = [FreeShipping()]
		data = {'status_code':200}
		# print('repository: get_available_shipping_methods \n ')
		if shipping_addr and shipping_addr.country.code in ['US', 'CA', 'MX']:

			weight = basket.total_weight
			# methods += self.shipstation_get_shipping_methods(basket, weight)
			methods,data = self.fedex_get_rates_and_transit_times(basket, weight, shipping_addr)
			###############################################################################
			## will need to implement some sort of API here to properly configure which  ##
			## shipping methods are available to a user based on their geo location      ##
			###############################################################################
			return methods,data

		return methods

	def get_city_and_state(self, postcode=None):
		# try:
		logger.debug(f'USPS API: Attempting to retrieve city/state information ({postcode})')
		data = {}
		BASE_URL = 'https://secure.shippingapis.com/ShippingAPI.dll?API=CityStateLookup'

		if not postcode:
			data['error'] = 'Bad Request'

		else:
			xml = f'<CityStateLookupRequest USERID="{settings.USPS_USERNAME}"><ZipCode ID= "0"><Zip5>{postcode}</Zip5></ZipCode></CityStateLookupRequest>'
			url = f"{BASE_URL}&XML={xml}"
			xml_response = requests.get(url).content
			usps_response = json.loads(json.dumps(xmltodict.parse(xml_response)))['CityStateLookupResponse']
			if 'Error' in usps_response['ZipCode'].keys():
				data['error'] = usps_response['ZipCode']['Error']
				logger.debug(f"USPS API [Error]: ({postcode}) {usps_response['ZipCode']['Error']}")

			else:
				data['city'] = usps_response['ZipCode']['City']
				data['line4'] = usps_response['ZipCode']['City']
				data['state'] = usps_response['ZipCode']['State']

		return data

	def get_postcode(self, address):
		zip5 = None
		BASE_API_URL = 'https://secure.shippingapis.com/ShippingAPI.dll?API=ZipCodeLookup'

		xml = f'<ZipCodeLookupRequest USERID="{settings.USPS_USERNAME}"><Address ID= "1"><Address1/><Address2>{address.line1}</Address2><City>{address.line4}</City>'

		xml += f'<State>{address.state}</State></Address></ZipCodeLookupRequest>'

		url = f"{BASE_API_URL}&XML={xml}"
		xml_response = requests.get(url).content
		usps_response = json.loads(json.dumps(xmltodict.parse(xml_response)))['ZipCodeLookupResponse']

		print('get_postcode usps_response: ', usps_response)
		if usps_response.get('Address') and usps_response['Address'].get('Zip5'):
			zip5 = usps_response['Address']['Zip5']

		return zip5



	def is_residential(self, address):
		validated_address = self.usps_validate_address(address)
		residential = True
		if validated_address.get('Business', None) and validated_address['Business']=='Y':
			residential = False

		return residential

	def make_address_corrections(self, address):
		corrections = {}
		validated_address = self.usps_validate_address(address)

		if not validated_address:
			return [address, None]

		if validated_address.get('Address2', None) and address.line1 != validated_address['Address2']:
			print(f'correcting line1 from {address.line1} to {validated_address["Address2"]}')
			address.line1 = corrections['line1'] = validated_address['Address2']

		if validated_address.get('City', None) and address.line4 != validated_address['City']:
			print(f'correcting city from {address.line4} to {validated_address["City"]}')
			address.line4 = corrections['line4'] = validated_address['City']

		if validated_address.get('Zip5', None) and address.postcode != validated_address['Zip5']:
			print(f'correcting postcode from {address.postcode} to {validated_address["Zip5"]}')
			address.postcode = corrections['postcode'] = validated_address['Zip5']

		if validated_address.get('State', None) and address.state and address.state != validated_address['State']:
			print(f'correcting State from {address.state} to {validated_address["State"]}')
			address.state = corrections['state'] = validated_address['State']

		residential = validated_address.get('Business', None)
		if residential:
			residential = True if residential == 'N' else False
			if hasattr(address, 'is_residential') and address.is_residential != residential:
				print(f'correcting residential status {address.is_residential} to {residential}')
				address.is_residential = residential


		return address,corrections


	def usps_validate_address(self, address):
		BASE_API_URL = 'https://secure.shippingapis.com/ShippingAPI.dll?API=Verify'

		xml = f'<AddressValidateRequest USERID="{settings.USPS_USERNAME}"><Revision>1</Revision><Address ID="0">'
		address1 = f'<Address1>{address.line2}</Address1>' if address.line2 else "<Address1/>"
		xml += address1
		xml += f'<Address2>{address.line1}</Address2>'
		xml += f'<City>{address.line4}</City>'
		xml += f'<State>{address.state}</State>'
		xml += f'<Zip5>{address.postcode}</Zip5><Zip4/>'

		xml += '</Address></AddressValidateRequest>'

		url = f"{BASE_API_URL}&XML={xml}"
		xml_response = requests.get(url).content
		usps_response = json.loads(json.dumps(xmltodict.parse(xml_response)))['AddressValidateResponse']['Address']

		if usps_response.get('Error'):
			return None

		return usps_response


	def coerce_shipstation_address(self, address):
		address_fields = {
			'name': address.name,
			'street1':address.line1,
			'city': address.line4,
			'postalCode': address.postcode,
			'country': address.country.iso_3166_1_a2,
		}
		if address.phone_number:
			address_fields['phone'] = address.phone_number.as_international
		if address.line2:
			address_fields['street2'] = address.line2
		if address.line3:
			address_fields['street3'] = address.line3
		if address.state:
			address_fields['state'] = address.state

		if hasattr(address, 'is_residential'):
			address_fields['residential'] = address.is_residential

		return address_fields


	def get_first_image_url(self, line):
		img = line.product.get_all_images().first()
		if not img:
			return None

		return img.original.url

	def shipstation_coerce_discounts(self, discounts):
		all_discounts = []
		for _discount in discounts:
			discount = {
				'sku':_discount.code,
				'name': _discount.name,
				'weight': {
					'value': 0,
					'units': 'pounds',
				},
				'quantity': 1,
				'unitPrice': str(_discount.total_discount * -1),
				'adjustment': True
			}

			all_discounts.append(discount)

		return all_discounts

	async def async_coerce_shipstation_line_items(self, lines, base_url=''):
		line_items = []
		for line in lines:
			print('line: ', line)
			line_dict = {
				'lineItemKey':line.partner_sku,
				'sku':line.partner_sku,
				'name': line.product.title,
				'weight': {
					'value': str(line.product.weight),
					'units': 'pounds',
				},
				'quantity': line.quantity,
				'unitPrice': str(line.unit_price_excl_tax),
				'taxAmount': str(line.unit_price_tax),
				'productId': line.product.id,
				'adjustment': False
			}

			image_url = await self.async_get_first_image_url(line)
			if image_url:
				image_url = settings.BASE_URL+image_url
				line_dict.update({'imageUrl': image_url})

			if line.product.is_child:
				line_dict.update({'name':line.product.parent.title, 'options':[{'name':'Size', 'value':line.product.title}]})

			line_items.append(line_dict)

		print('line_items: ', line_items)

		return line_items


	async def async_fetch_order_weight(self, order):
		basket = await self.async_fetch_basket_with_related(order.basket.id)
		return basket.total_weight

	def fetch_basket_with_related(self, basket_id):
		return Basket.objects.prefetch_related('lines').get(id=basket_id)

	def fetch_line_with_related(self, line):
		pass

	def fetch_order_lines_with_related(self, order):
		return list(order.lines.select_related('product__parent').prefetch_related('prices', 'product__images').all())

	def fetch_discounts_with_related(self, order):
		# return list(order.discounts.select_related('voucher_set').prefetch_related('offers').all())
		return list(order.discounts.prefetch_related('offers').all())

	def fetch_order_with_related(self, order_id):
		return Order.objects.select_related('billing_address__country', 'shipping_address__country', 'basket', 'user').prefetch_related('lines', 'discounts', 'basket__lines__product').get(id=order_id)

	def fetch_shipping_cost(self, order):
		return order.shipping_before_discounts_incl_tax

	async def async_shipstation_place_order(self, order, request=None):

		order = await self.async_fetch_order_with_related(order.id)
		lines = await self.async_fetch_order_lines_with_related(order)
		customer_email = order.user.email if order.user else order.guest_email

		billing_address = await self.async_coerce_shipstation_address(order.billing_address)
		shipping_address = await self.async_coerce_shipstation_address(order.shipping_address)

		base_url = get_current_site(request) if request else ''

		items = await self.async_coerce_shipstation_line_items(lines, base_url)
		shipping_cost = await self.async_fetch_shipping_cost(order)
		# total_weight = await self.async_fetch_order_weight(order)
		payload = {
			"orderNumber": order.id+10000,
			"orderKey": order.number,
			"orderDate": datetime.datetime.now().isoformat(),
			"paymentDate": datetime.datetime.now().isoformat(),
			"orderStatus": "awaiting_shipment",
			"customerEmail": customer_email,
			"billTo": billing_address,
			"shipTo": shipping_address,
			"items": items,
			"amountPaid": str(order.total_incl_tax),
			"taxAmount": str(order.total_tax),
			"shippingAmount": str(shipping_cost),
			"carrierCode": "fedex",
			"serviceCode": order.shipping_code.lower(),
			"weight": {
				"value": str(D(order.basket.total_weight).quantize(TWOPLACES)),
				"units": "pounds"
			},
		}

		discounts = await self.async_fetch_discounts_with_related(order)

		if len(discounts):
			items += await self.shipstation_coerce_discounts(discounts)
			payload.update({'items': items})

		if order.shipping_address.notes:
			payload.update({'internalNotes': order.shipping_address.notes})

		url = "https://ssapi.shipstation.com/orders/createorder"
		headers = self.shipstation_get_headers()
		print('attempting to place shipstation order')
		logger.debug('attempting to place shipstation order')

		shipstation_response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
		msg = f'shipstation order placed: {shipstation_response} {shipstation_response.text}'
		logger.debug(msg)
		print(msg)

		return shipstation_response

	async_get_first_image_url = sync_to_async(get_first_image_url)
	async_shipstation_coerce_discounts = sync_to_async(shipstation_coerce_discounts)
	async_coerce_shipstation_address = sync_to_async(coerce_shipstation_address)
	async_usps_validate_address = sync_to_async(usps_validate_address)
	async_fetch_order_with_related = sync_to_async(fetch_order_with_related)
	async_fetch_order_lines_with_related = sync_to_async(fetch_order_lines_with_related)
	async_fetch_discounts_with_related = sync_to_async(fetch_discounts_with_related)
	async_fetch_shipping_cost = sync_to_async(fetch_shipping_cost)
	async_fetch_basket_with_related = sync_to_async(fetch_basket_with_related)

	async def shipstation_get_response(url, payload, headers, data):
		pass

	def fedex_get_customs_clearance_details(self, basket):
		total_cost = str(basket.total_excl_tax_excl_discounts)
		weight = basket.total_weight
		customs_obj = {
			'commercialInvoice': {
				'shipmentPurpose': 'SOLD',
			},
			'freightOnValue': 'CARRIER_RISK',
			'dutiesPayment': {
				'paymentType': 'SENDER'
			},
			'commodities': [{
				'description': 'DRIED COCKTAIL GARNISHES',
				'weight': {
					'units': 'LB',
					'value': weight,
				},
				'quantity': 1,
				'customsValue': {
					'amount': total_cost,
					'currency': 'USD',
				},
				'numberOfPieces': 1,
				'countryOfManufacture': 'US',
				'harmonizedCode': '080510',
				'name': 'DRIED GARNISHES',

			}]
		}
		return customs_obj

		# https://developer.fedex.com/api/en-us/catalog/rate/v1/docs.html#operation/Rate%20and%20Transit%20times

	def get_free_shipping(self):
		return FreeShipping()

	def fedex_validate_address(self, shipping_addr):
		street_lines = [x for x in [shipping_addr.line1, shipping_addr.line2, shipping_addr.line3] if x]
		to_address = {
			"streetLines": street_lines,
			"postalCode": shipping_addr.postcode,
			"city": shipping_addr.line4,
			"stateOrProvinceCode":shipping_addr.state,
			"countryCode": shipping_addr.country.code,
		}
		payload = {
			'addressesToValidate': [
				{
					'address': to_address
				}
			]
		}

		headers = {
			'Content-Type': "application/json",
			'X-locale': "en_US",
			'Authorization': "Bearer " + self.fedex_get_auth_token()
		}
		url = settings.FEDEX_API_URL + "address/v1/addresses/resolve"
		response = requests.post(url, data=json.dumps(payload), headers=headers)
		status_code = response.status_code

	def fedex_get_rates_and_transit_times(self, basket, weight, shipping_addr, max_retries=1):
		# shipping_addr = usps_validate_address(shipping_addr)
		methods = []
		data = {'status_code': 200}
		retries = 0
		street_lines = [x for x in [shipping_addr.line1, shipping_addr.line2, shipping_addr.line3] if x]
		if not shipping_addr.is_validated and shipping_addr.country.iso_3166_1_a2.upper()=='US':


			shipping_addr,corrections = self.make_address_corrections(shipping_addr)
			if corrections:
				data.update({'corrections':corrections})

		to_address = {
			"streetLines": street_lines,
			"postalCode": shipping_addr.postcode,
			"city": shipping_addr.line4,
			"stateOrProvinceCode":shipping_addr.state,
			"countryCode": shipping_addr.country.code,
		}

		if hasattr(shipping_addr, 'is_residential'):
			to_address.update({'residential':shipping_addr.is_residential})

		ship_date = datetime.date.today()
		if datetime.datetime.now().hour > 19:

			ship_date += datetime.timedelta(days=1)

		ship_date = ship_date.isoformat()
		payload = {
			"accountNumber": {
				"value":settings.FEDEX_ACCOUNT_NUMBER
			},
			"carrierCodes": ["FDXE", "FDXG"],
			"rateRequestControlParameters": {
				"returnTransitTimes": True,
				"rateSortOrder": "COMMITASCENDING"
			},
			"requestedShipment": {
				"shipDateStamp": ship_date,
				"shipper": {
					"address": {
						"streetLines": [
							"512 Rio Grande St"
						],
						"city":"AUSTIN",
						"stateOrProvinceCode":"TX",
						"postalCode": int(settings.HOME_POSTCODE),
						"countryCode": "US",
						"residential": False
					}
				},
				"recipient": {
					"address": to_address
				},
				"pickupType": "DROPOFF_AT_FEDEX_LOCATION",
				"rateRequestType": [
					"LIST",
				],
				"requestedPackageLineItems": [
					{
					"weight": {
						"units": "LB",
						"value": weight
					}
				  }
			  ]
			}
		}

		if shipping_addr.country.code.upper() != 'US':
			payload['requestedShipment'].update({'customsClearanceDetail': self.fedex_get_customs_clearance_details(basket)})

		headers = {
			'Content-Type': "application/json",
			'X-locale': "en_US",
			'Authorization': "Bearer " + self.fedex_get_auth_token()
		}
		url = settings.FEDEX_API_URL + "rate/v1/rates/quotes"
		response = requests.post(url, data=json.dumps(payload), headers=headers)

		status_code = response.status_code
		if status_code == 200:

			## do something with the response text
			response_list = json.loads(response.text)

			for rate in response_list['output']['rateReplyDetails']:

				if len(rate['ratedShipmentDetails']) < 1:
					continue

				cost = rate['ratedShipmentDetails'][0]['totalNetCharge']
				try:
					arrival = datetime.datetime.fromisoformat(rate['commit']['dateDetail']['dayFormat'])
				except Exception as e:
					print('dateDetail not found... this is what the object contains: ', rate['commit'])
					arrival = datetime.datetime.now().isoformat()


				methods.append(
					BaseFedex(code=rate['serviceType'], arrival=arrival, name=rate['serviceName'], charge_excl_tax=cost, charge_incl_tax=cost)
				)
		else:
			response_text = json.loads(response.text)
			error = response_text['errors'][0]
			# error_code = errors[0]['code']
			print('Error message: ', error['message'])
			print('Error code: ', error['code'])

			logger.error(f'Fedex API error with status code: {status_code}. \n{error["message"]}')

			if error['code'] == 'CRSVZIP.CODE.INVALID':
				print('invalid zip code')
				if retries < max_retries:
					shipping_addr,corrections = self.make_address_corrections(shipping_addr)
					methods,_data = self.fedex_get_rates_and_transit_times(basket, weight, shipping_addr)
					if _data:
						data.update(_data)

					if corrections:
						data.update({'corrections': corrections})


			if status_code == 400:
				print('\n BAD REQUEST')

			elif status_code == 403:
				print('\n FORBIDDEN')

			elif status_code == 404:
				print('\n NOT FOUND')

			elif status_code == 429:
				print('\n RATE LIMITED')

			elif status_code == 500:
				print('\n FAILURE')

			elif status_code == 503:
				print('\n SERVICE UNAVAILABLE')

				print(' *** ATTEMPTING TO GET METHODS FROM SHIPSTATION ***')

				methods, _data = self.shipstation_get_shipping_methods(weight, shipping_addr)
				if _data:
					data.update(_data)


		return methods, data



	def fedex_update_auth_token(self, FedexAuthToken=FedexAuthTokenModel.objects.first()):

		payload = f"grant_type=client_credentials&client_id={settings.FEDEX_API_KEY}&client_secret={settings.FEDEX_SECRET_KEY}"
		url = settings.FEDEX_API_URL + "oauth/token"

		headers = {
			'Content-Type': "application/x-www-form-urlencoded"
		}

		response = requests.post(url, data=payload, headers=headers)
		response_text = json.loads(response.text)

		status_code = response.status_code
		if status_code == 200:

			FedexAuthToken.access_token = response_text["access_token"]
			FedexAuthToken.scope = response_text["scope"]
			FedexAuthToken.expires_in = response_text["expires_in"]
			FedexAuthToken.save()

		else:

			error = response_text['errors'][0]
			logger.error(f'Fedex API: Error authorizing ({status_code}). \n{error["message"]}')

			if status_code == 400:
				print('\n BAD REQUEST')

			elif status_code == 401:
				print('\n UNAUTHORIZED')

			elif status_code == 403:
				print('\n FORBIDDEN')

			elif status_code == 404:
				print('\n NOT FOUND')

			elif status_code == 429:
				print('\n RATE LIMITED')

			elif status_code == 500:
				print('\n INTERNAL.SERVER.ERROR')

			elif status_code == 503:
				print('\n SERVICE UNAVAILABLE')

		return FedexAuthToken

	def fedex_get_auth_token(self):

		FedexAuthToken = FedexAuthTokenModel.objects.first()

		if not FedexAuthToken:
			FedexAuthToken = FedexAuthTokenModel.objects.create()
			FedexAuthToken.save()
			self.fedex_update_auth_token(FedexAuthToken)

		if FedexAuthToken.expired:
			self.fedex_update_auth_token(FedexAuthToken)

		return FedexAuthToken.access_token

	def shipstation_get_headers(self):
		SHIPSTATION_AUTH_STR = bytes(f"{settings.SHIPSTATION_API_KEY}:{settings.SHIPSTATION_SECRET_KEY}", encoding='utf-8')
		SHIPSTATION_AUTH_KEY = base64.b64encode(SHIPSTATION_AUTH_STR)
		AUTH_TOKEN = f"Basic {SHIPSTATION_AUTH_KEY.decode()}"

		headers = {
		  'Host': 'ssapi.shipstation.com',
		  'Authorization': AUTH_TOKEN,
		  'Content-Type': 'application/json'
		}

		return headers

	def shipstation_get_response(self, url, payload, headers=None):
		headers = self.shipstation_get_headers() if not headers else headers
		shipstation_response = requests.request("POST", url, headers=self.shipstation_get_headers(), data=json.dumps(payload))
		response = requests.post(url, headers=headers, data=json.dumps(payload))
		return response

	def shipstation_get_shipping_methods(self, weight, shipping_addr):

		# documentation: https://www.shipstation.com/docs/api/shipments/get-rates/
		methods = []
		data = {}
		payload = {
			"carrierCode":"fedex",
			"serviceCode": None,
			"packageCode": None,
			"fromPostalCode": settings.HOME_POSTCODE,
			"toState": shipping_addr.state,
			"toCountry":shipping_addr.country.code,
			"toPostalCode":shipping_addr.postcode,
			"toCity": shipping_addr.line4,
			"weight": {
				"value": str(weight),
				"units":"pounds"
			},
			"confirmation": "none",
			"residential": False
		}
		#
		url = "https://ssapi.shipstation.com/shipments/getrates"
		#
		# shipstation_response = requests.request("POST", url, headers=self.shipstation_get_headers(), data=json.dumps(payload))
		response = self.shipstation_get_response(url, payload)

		status_code = response.status_code
		# request was good, create the methods
		if status_code == 200:

			response_list = json.loads(response.text)
			for item in response_list:

				methods.append(
					BaseFedex(item['serviceCode'], item['serviceName'], item['shipmentCost'], item['shipmentCost'])
				)

		else:
			response_text = json.loads(response.text)
			error = response_text['errors'][0]
			logger.error(f'Shipstation API: Error retrieving shipping methods ({status_code}). \n{error["message"]}')

			# error_code = errors[0]['code']
			print('Error retrieving shipping methods from shipstation')
			print('Error message: ', error['message'])
			print('Error code: ', error['code'])

			if status_code == 400:
				print('\n BAD REQUEST')

			if status_code == 403:
				print('\n FORBIDDEN')

			if status_code == 404:
				print('\n NOT FOUND')

			elif status_code == 429:
				print('\n RATE LIMITED')

			elif status_code == 500:
				print('\n FAILURE')

			elif status_code == 503:
				print('\n SERVICE UNAVAILABLE')

		data.update({'status_code': status_code})
		return methods, data

repository = Repository()