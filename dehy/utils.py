from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six, base64, requests, json
from dehy.appz.shipping.methods import BaseFedex, FreeShipping
from dehy.appz.generic.models import FedexAuthToken as FedexAuthTokenModel
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from jose import jwk

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from oscar.core.loading import get_class, get_model
QuickbooksAuthToken = get_model('generic', 'QuickbooksAuthToken')

class TokenGenerator(PasswordResetTokenGenerator):

	def _make_hash_value(self, user, timestamp):
		return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_email_verified))


generate_token = TokenGenerator()

# takes a dict and returns it without any items containing empty values
def clear_empty_dict_items(_dict):
	return {k: v for k, v in _dict.items() if v}

def string_to_base64(s):
	return base64.b64encode(bytes(s, 'utf-8')).decode()

def get_discovery_document():
	response = requests.get(settings.QUICKBOOKS_DISCOVERY_DOCUMENT_URL)
	if response.status_code >= 400:
		return ''

	discovery_doc_json = response.json()
	discovery_doc = OAuth2Config(
		issuer=discovery_doc_json['issuer'],
		auth_endpoint=discovery_doc_json['authorization_endpoint'],
		userinfo_endpoint=discovery_doc_json['userinfo_endpoint'],
		revoke_endpoint=discovery_doc_json['revocation_endpoint'],
		token_endpoint=discovery_doc_json['token_endpoint'],
		jwks_uri=discovery_doc_json['jwks_uri'])

	return discovery_doc

class QuickBooks(object):
	def __init__(self, *args, **kwargs):
		self.api_key = settings.QUICKBOOKS_API_KEY
		self.secret_key = settings.QUICKBOOKS_SECRET_KEY
		self.discovery_document = get_discovery_document()
		self.redirect_uri = settings.QUICKBOOKS_REDIRECT_URI
		self.base_url = settings.QUICKBOOKS_BASE_URL
		self.environment = settings.QUICKBOOKS_ENVIRONMENT
		self.auth_token = QuickbooksAuthToken.objects.get()
		self.auth_client = AuthClient(
			self.api_key, self.secret_key, self.redirect_uri, self.environment,
			realm_id=self.auth_token.realm_id, access_token=self.auth_token.access_token,
			refresh_token=self.auth_token.refresh_token,
		)


		self.refresh_auth_token()

	def update_auth_token(self):
		self.auth_token.access_token = self.auth_client.access_token
		self.auth_token.refresh_token = self.auth_client.refresh_token
		self.auth_token.save()

	def api_call(self, call_name='customer', payload={}):
		url = self.base_url + f'/v3/company/{self.auth_client.realm_id}/{call_name}?minorversion=65'
		auth_header = 'Bearer {0}'.format(self.auth_client.access_token)
		headers = {
		    'Authorization': auth_header,
		    'Accept': 'application/json'
		}

		response = request.post(url, data=payload, headers=headers)
		return response

	def refresh_auth_token(self):
		self.auth_client.refresh()
		self.update_auth_token()


	@property
	def auth_header(self):
		return 'Basic ' + string_to_base64(self.api_key + ':' + self.secret_key)

	def get_company_info(self, access_token, realm_id):
		route = '/v3/company/{0}/companyinfo/{0}'.format(realm_id)
		auth_header = 'Bearer ' + access_token
		headers = {'Authorization': auth_header, 'accept': 'application/json'}
		response = requests.get(settings.QUICKBOOKS_BASE_URL + route, headers=headers)
		status_code = response.status_code
		if status_code != 200:
			response = ''
			return response, status_code

		response = json.loads(response.text)
		return response, status_code

	def update_session(self, request, access_token, refresh_token, realm_id, name=None):
		request.session['access_token'] = access_token
		request.session['refresh_token'] = refresh_token
		request.session['realm_id'] = realm_id
		request.session['name'] = name

	def revoke_token(self):
		revoke_endpoint = self.discovery_document.revoke_endpoint
		headers = {'Accept': 'application/json', 'content-type': 'application/json', 'Authorization': self.auth_header}
		payload = {'token': token}
		response = requests.post(revoke_endpoint, json=payload, headers=headers)

	def get_bearer_token(self, auth_code):
		token_endpoint = self.discovery_document.token_endpoint
		headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',
				   'Authorization': self.auth_header}
		payload = {
			'code': auth_code,
			'redirect_uri': settings.REDIRECT_URI,
			'grant_type': 'authorization_code'
		}
		response = requests.post(token_endpoint, data=payload, headers=headers)
		if response.status_code != 200:
			return response.text
		bearer_raw = json.loads(response.text)

		if 'id_token' in bearer_raw:
			id_token = bearer_raw['id_token']
		else:
			id_token = None

		return Bearer(bearer_raw['x_refresh_token_expires_in'], bearer_raw['access_token'], bearer_raw['token_type'],
					  bearer_raw['refresh_token'], bearer_raw['expires_in'], id_token=id_token)

	def validate_jwt_token(self, token):
		current_time = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
		token_parts = token.split('.')
		id_token_header = json.loads(base64.b64decode(token_parts[0]).decode('ascii'))
		id_token_payload = json.loads(base64.b64decode(self.incorrect_padding(token_parts[1])).decode('ascii'))

		if id_token_payload['iss'] != settings.ID_TOKEN_ISSUER:
			return False
		elif id_token_payload['aud'][0] != settings.CLIENT_ID:
			return False
		elif id_token_payload['exp'] < current_time:
			return False

		token = token.encode()
		token_to_verify = token.decode("ascii").split('.')
		message = token_to_verify[0] + '.' + token_to_verify[1]
		id_token_signature = base64.urlsafe_b64decode(self.incorrect_padding(token_to_verify[2]))

		keys = self.get_key_from_jwk_url(id_token_header['kid'])

		public_key = jwk.construct(keys)
		return public_key.verify(message.encode('utf-8'), id_token_signature)

	def incorrect_padding(self, s):
		return s + '=' * (4 - len(s) % 4)

	def get_key_from_jwk_url(self, kid):
		jwk_uri = self.discovery_document.jwks_uri
		response = requests.get(jwk_uri)
		if response.status_code >= 400:
			return ''
		data = json.loads(response.text)
		key = next(ele for ele in data["keys"] if ele['kid'] == kid)

		return key

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


class Bearer(object):
	def __init__(self, refresh_expiry, access_token, token_type, refresh_token, access_token_expiry, id_token=None):
		self.refresh_expiry = refresh_expiry
		self.access_token = access_token
		self.token_type = token_type
		self.refresh_token = refresh_token
		self.access_token_expiry = access_token_expiry
		self.id_token = id_token


class OAuth2Config(object):
	def __init__(self, issuer='', auth_endpoint='', token_endpoint='', userinfo_endpoint='', revoke_endpoint='', jwks_uri=''):
		self.issuer = issuer
		self.auth_endpoint = auth_endpoint
		self.token_endpoint = token_endpoint
		self.userinfo_endpoint = userinfo_endpoint
		self.revoke_endpoint = revoke_endpoint
		self.jwks_uri = jwks_uri


# quickbooks = qb = QuickBooks()