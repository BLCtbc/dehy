from oscar.apps.shipping import repository
from dehy.appz.shipping import methods as _shipping_methods
from dehy.appz.shipping.methods import BaseFedex
from dehy.appz.generic.models import FedexAuthToken as FedexAuthTokenModel

import base64, json, requests
from oscar.core.loading import get_class
from django.conf import settings

SHIPSTATION_AUTH_STR = bytes(f"{settings.SHIPSTATION_API_KEY}:{settings.SHIPSTATION_SECRET_KEY}", encoding='utf-8')
SHIPSTATION_AUTH_KEY = base64.b64encode(SHIPSTATION_AUTH_STR)
AUTH_TOKEN = f"Basic {SHIPSTATION_AUTH_KEY.decode()}"

# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods

# class Repository(repository.Repository):
# 	methods = (shipping_methods.Standard(), shipping_methods.Express())

class Repository(repository.Repository):

	def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
		methods = [_shipping_methods.FreeShipping()]
		status_code = 200
		# print('repository: get_available_shipping_methods \n ')

		if shipping_addr:
			print('\n *** shipping_addr: ', shipping_addr)

		if shipping_addr and shipping_addr.country.code in ['US', 'CA', 'MX']:

			weight = basket.total_weight
			# methods += self.get_shipstation_shipping_methods(basket, weight)
			methods,status_code = self.fedex_get_rates_and_transit_times(basket, weight, shipping_addr)
			###############################################################################
			## will need to implement some sort of API here to properly configure which  ##
			## shipping methods are available to a user based on their geo location      ##
		 	###############################################################################
			return methods,status_code

		return methods

	def fedex_get_rates_and_transit_times(self, basket, weight, shipping_addr):
		print('\n **** GETTING FEDEX RATES **** ')
		methods = []
		street_lines = [x for x in [shipping_addr.line1, shipping_addr.line2, shipping_addr.line3] if x]
		payload={
		  "accountNumber": {
		    "value": settings.FEDEX_ACCOUNT_NUMBER
		  },
		  "carrierCodes": ["FDXE", "FDXG"],
		  "rateRequestControlParameters": {
		  	"returnTransitTimes": True,
			"rateSortOrder": "COMMITASCENDING"
		  },
		  "requestedShipment": {
		    "shipper": {
		      "address": {
				"streetLines": [
					"512 Rio Grande St"
				],
				"city":"Austin",
				"stateOrProvinceCode":"TX",
		        "postalCode": int(settings.HOME_POSTCODE),
		        "countryCode": "US"
		      }
		    },
			"recipient": {
			  "address": {
			  "streetLines": street_lines,
				"postalCode": shipping_addr.postcode,
				"city": shipping_addr.line4,
				"stateOrProvinceCode":shipping_addr.state,
				"countryCode": shipping_addr.country.code
			  }
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

		headers = {
		    'Content-Type': "application/json",
		    'X-locale': "en_US",
		    'Authorization': "Bearer " + self.get_fedex_auth_token()
		}
		url = settings.FEDEX_API_URL + "rate/v1/rates/quotes"
		response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

		print('response.status_code: ', response.status_code)
		if response.status_code == 200:

			## do something with the response text
			response_list = json.loads(response.text)

			for rate in response_list['output']['rateReplyDetails']:
				cost = rate['ratedShipmentDetails'][0]['totalNetCharge']

				methods.append(
					BaseFedex(code=rate['serviceType'], name=rate['serviceName'], charge_excl_tax=cost, charge_incl_tax=cost)
				)
		else:

			response_text = json.loads(response.text)
			error = response_text['errors'][0]
			# error_code = errors[0]['code']
			print('Error message: ', error['message'])
			print('Error code: ', error['code'])

			if response.status_code == 400:
				print('\n BAD REQUEST')

			if response.status_code == 403:
				print('\n FORBIDDEN')

			if response.status_code == 404:
				print('\n NOT FOUND')

			elif response.status_code == 429:
				print('\n RATE LIMITED')

			elif response.status_code == 500:
				print('\n FAILURE')

			elif response.status_code == 503:
				print('\n SERVICE UNAVAILABLE')



		return methods, response.status_code



	def update_fedex_auth_token(self, FedexAuthToken=FedexAuthTokenModel.objects.first()):

		payload = f"grant_type=client_credentials&client_id={settings.FEDEX_API_KEY}&client_secret={settings.FEDEX_SECRET_KEY}"
		url = settings.FEDEX_API_URL + "oauth/token"

		headers = {
			'Content-Type': "application/x-www-form-urlencoded"
		}

		response = requests.request("POST", url, data=payload, headers=headers)
		response_text = json.loads(response.text)


		if response.status_code == 200:

			FedexAuthToken.access_token = response_text["access_token"]
			FedexAuthToken.scope = response_text["scope"]
			FedexAuthToken.expires_in = response_text["expires_in"]
			FedexAuthToken.save()

		elif response.status_code == 401:
			print('Unauthorized')

		elif response.status_code == 429:
			print('rate limited')

		elif response.status_code == 500:
			print('INTERNAL.SERVER.ERROR')

		elif response.status_code == 503:
			print('INTERNAL.SERVER.ERROR')


		return FedexAuthToken

	def get_fedex_auth_token(self):

		FedexAuthToken = FedexAuthTokenModel.objects.first()

		if not FedexAuthToken:
			FedexAuthToken = FedexAuthTokenModel.objects.create()
			FedexAuthToken.save()
			self.update_fedex_auth_token(FedexAuthToken)

		if FedexAuthToken.expired:
			self.update_fedex_auth_token(FedexAuthToken)

		return FedexAuthToken.access_token




	def get_shipstation_shipping_methods(self, basket, weight):
		methods = []
		payload = {
			"carrierCode":"fedex",
			"serviceCode": None,
			"packageCode": None,
			"fromPostalCode": settings.HOME_POSTCODE,
			"toState":"TX",
			"toCountry":"US",
			"toPostalCode":"78701",
			"toCity": "Austin",
			"weight": {
				"value": weight,
				"units":"lbs"
			},
			"confirmation": "none",
			"residential": False
		}

		shipstation_headers = {
		  'Host': 'ssapi.shipstation.com',
		  'Authorization': AUTH_TOKEN,
		  'Content-Type': 'application/json'
		}

		url = "https://ssapi.shipstation.com/shipments/getrates"

		shipstation_response = requests.request("POST", url, headers=shipstation_headers, data=json.dumps(payload))

		# request was good, return
		if shipstation_response.status_code == 200:

			response_list = json.loads(shipstation_response.text)
			for item in response_list:

				methods.append(
					BaseFedex(item['serviceCode'], item['serviceName'], item['shipmentCost'], item['shipmentCost'])
				)

		return methods