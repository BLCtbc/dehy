from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from dehy.appz.shipping.methods import BaseFedex, FreeShipping
from dehy.appz.generic.models import FedexAuthToken as FedexAuthTokenModel
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

class TokenGenerator(PasswordResetTokenGenerator):

	def _make_hash_value(self, user, timestamp):
		return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_email_verified))


generate_token = TokenGenerator()

# takes a dict and returns it without any items containing empty values
def clear_empty_dict_items(_dict):
	return {k: v for k, v in _dict.items() if v}


class Fedex(object):


	def __init__(self, *args, **kwargs):
		self.base_url = settings.FEDEX_API_URL
		self.secret_key = settings.FEDEX_SECRET_KEY
		self.api_key = settings.FEDEX_API_KEY


	def update_auth_token(self, auth_token=FedexAuthTokenModel.objects.first()):

		payload = f"grant_type=client_credentials&client_id={settings.FEDEX_API_KEY}&client_secret={settings.FEDEX_SECRET_KEY}"
		url = self.base_url + "oauth/token"

		headers = {
			'Content-Type': "application/x-www-form-urlencoded"
		}

		response = requests.request("POST", url, data=payload, headers=headers)
		response_text = json.loads(response.text)

		status_code = response.status_code
		if status_code == 200:

			auth_token.access_token = response_text["access_token"]
			auth_token.scope = response_text["scope"]
			auth_token.expires_in = response_text["expires_in"]
			auth_token.save()

		else:
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

		return auth_token

	def get_auth_token(self):

		auth_token = FedexAuthTokenModel.objects.first()

		if not AuthToken:
			auth_token = FedexAuthTokenModel.objects.create()
			auth_token.save()
			self.update_fedex_auth_token(auth_token)

		if auth_token.expired:
			self.update_fedex_auth_token(auth_token)

		return auth_token.access_token

	def validate_address(self):
		pass

	def get_rates_and_transit_times(self):
		pass


	def check_address_validity(self, address):
		"""
		Checks an address has correct fields required for a Fedex request,
		such as the presence of a country object
		"""
		pass

	def make_address_corrections(self, address):
		corrections = {}
		validated_address = self.validate_address(address)

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