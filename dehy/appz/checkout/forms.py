from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from oscar.apps.customer.utils import normalise_email
from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_model
from oscar.forms.mixins import PhoneNumberMixin
from oscar.apps.payment import forms as payment_forms
from django.db.models import Q

User = get_user_model()
AbstractAddressForm = get_class('address.forms', 'AbstractAddressForm')
Country = get_model('address', 'Country')
AdditionalInfoQuestionaire = get_class('dehy.appz.generic.models', 'AdditionalInfoQuestionnaire')
CoreBillingAddressForm = get_class('payment.forms', 'BillingAddressForm')
BillingAddress = get_model('order', 'BillingAddress')

class PurchaseConfirmationForm(forms.Form):
	create_new_account = forms.BooleanField(label=_("Create an account for faster checkout"), required=True, initial=False)
	remember_payment_info = forms.BooleanField(label=_("Remember my payment information"), required=False, initial=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['remember_payment_info'].widget.attrs['hidden'] = True


class StripeTokenForm(forms.Form):
	stripeEmail = forms.EmailField(widget=forms.HiddenInput())
	stripeToken = forms.CharField(widget=forms.HiddenInput())

class BaseAddressForm(PhoneNumberMixin, AbstractAddressForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs['placeholder'] = _('First name')
		self.fields['last_name'].widget.attrs['placeholder'] = _('Last name')
		self.fields['state'].widget.attrs['placeholder'] = _('State')
		self.fields['line1'].widget.attrs['placeholder'] = _('Address 1')
		self.fields['line2'].widget.attrs['placeholder'] = _('Address 2')
		self.fields['line4'].widget.attrs['placeholder'] = _('City')
		self.fields['country'].widget.attrs['placeholder'] = _('Country')
		self.fields['postcode'].widget.attrs['placeholder'] = _('ZIP Code')
		self.fields['phone_number'].widget.attrs['placeholder'] = _('Phone Number')

class ShippingAddressForm(BaseAddressForm):
	required_fields = []
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.adjust_country_field()
		self.adjust_required_fields()
		# self.fields['phone_number'].required = False

	def get_required_fields(self):
		return self.required_fields

	def adjust_required_fields(self):
		required_fields = self.get_required_fields()
		if required_fields:
			for field_name,field in self.fields.items():
				self.fields[field_name].required = True if field_name in required_fields else False

	def adjust_country_field(self):
		countries = Country._default_manager.filter(Q(iso_3166_1_a2='US')|Q(iso_3166_1_a2='CA'))

		# No need to show country dropdown if there is only one option
		if len(countries) == 1:
			self.fields.pop('country', None)
			self.instance.country = countries[0]
		else:
			self.fields['country'].queryset = countries
			self.fields['country'].empty_label = None

	class Meta:
		model = get_model('order', 'ShippingAddress')
		fields = [
			'first_name', 'last_name',
			'line1', 'line2', 'line4',
			'state', 'postcode', 'country',
			'phone_number',
		]

class CountryAndPostcodeForm(ShippingAddressForm):
	required_fields = ['country', 'postcode']

class ShippingMethodForm(forms.Form):

	method_code = forms.ChoiceField(widget=forms.widgets.RadioSelect)

	def __init__(self, *args, **kwargs):
		methods = kwargs.pop('methods', [])
		super().__init__(*args, **kwargs)
		self.fields['method_code'].choices = ((m.code, m.name) for m in methods)


class AdditionalInfoForm(forms.ModelForm):
	# purchase_source = forms.ChoiceField(widget=forms.widgets.RadioSelect)

	class Meta:
		model = AdditionalInfoQuestionaire
		fields = '__all__'

class GatewayForm(AuthenticationForm):
	username = forms.EmailField(label=_("My email address is"))

class UserInfoForm(AuthenticationForm):
	username = forms.EmailField(label=_("Email"), help_text=_("You'll receive receipts and notifications at this email address."))
	signup = forms.BooleanField(initial=True, required=False, label=_("Subscribe to our mailing list to learn about new products and promotions!"))


	def __init__(self, *args, **kwargs):


		super().__init__(*args, **kwargs)

		self.fields['username'].widget.attrs.update({'placeholder':'username@email.com', 'autofill':'email'})

	class Meta:
		fields = ['username', 'signup']

	def clean_username(self):
		return normalise_email(self.cleaned_data['username'])

	def clean(self):
		if 'password' in self.errors:
			del self.errors['password']

		if 'username' in self.cleaned_data:
			email = normalise_email(self.cleaned_data['username'])
			if User._default_manager.filter(email__iexact=email).exists():

				msg = _("A user with that email address already exists")
				self._errors["username"] = self.error_class([msg])


		return super().clean()



class BaseBillingAddressForm(payment_forms.BillingAddressForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		print('attrs: ', self.fields['first_name'].widget.attrs)
		print('required: ', self.fields['first_name'].required)
		print('visible_fields: ', self.visible_fields())


		self.fields['first_name'].widget.attrs['placeholder'] = _('First name')
		self.fields['last_name'].widget.attrs['placeholder'] = _('Last name')
		self.fields['state'].widget.attrs['placeholder'] = _('State')
		self.fields['line1'].widget.attrs['placeholder'] = _('Address 1')
		self.fields['line2'].widget.attrs['placeholder'] = _('Address 2')
		self.fields['line4'].widget.attrs['placeholder'] = _('City')
		self.fields['country'].widget.attrs['placeholder'] = _('Country')
		self.fields['postcode'].widget.attrs['placeholder'] = _('ZIP Code')



	def adjust_country_field(self):

		countries = Country._default_manager.all()

		# No need to show country dropdown if there is only one option
		if len(countries) == 1:
			self.fields.pop('country', None)
			self.instance.country = countries[0]
		else:
			self.fields['country'].queryset = countries
			self.fields['country'].empty_label = None

	class Meta:
		model = BillingAddress
		fields = [
			'first_name', 'last_name',
			'line1', 'line2', 'line4',
			'state', 'postcode', 'country'
		]

class BillingAddressForm(BaseBillingAddressForm):
	same_as_shipping = forms.BooleanField(required=False, initial=True, label='Use shipping address')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['phone_number'].widget.attrs['placeholder'] = _('Phone Number')
		self.fields['phone_number'].required = False

	class Meta:
		model = BillingAddress
		fields = [
			'same_as_shipping',
			'first_name', 'last_name',
			'line1', 'line2', 'line4',
			'state', 'postcode', 'country'
		]


	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	# 	required_fields = ['country', 'postcode']
	# 	for field_name,field in self.fields.items():
	# 		self.fields[field_name].required = True if field_name in required_fields else False

