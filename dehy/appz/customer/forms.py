import datetime
from django import forms

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from oscar.core.loading import get_class, get_model

from oscar.apps.customer.forms import EmailAuthenticationForm as BaseEmailAuthenticationForm
from oscar.apps.customer.forms import EmailUserCreationForm as BaseEmailUserCreationForm
from dehy.appz.checkout.forms import ShippingAddressForm

Country = get_model('address', 'Country')

class EmailAuthenticationForm(BaseEmailAuthenticationForm):
	username = forms.EmailField(label=_('Email'))

class EmailUserCreationForm(BaseEmailUserCreationForm):

	first_name = forms.CharField(label=_('First Name'), required=True)
	last_name = forms.CharField(label=_('Last Name'), required=True)
	email = forms.EmailField(label=_('Email'))
	field_order = ['first_name', 'last_name', 'email', 'password1', 'password2']

def year_choices(max_year=0):
	current_year = datetime.date.today().year
	max_year = max_year if max_year else current_year+10
	return [(r,r) for r in range(current_year, max_year)]

class PaymentUpdateForm(ShippingAddressForm):
	required_fields = ['first_name', 'last_name', 'country', 'postcode', 'line4']
	month_choices = [(r,r) for r in range(1, 13)]
	exp_year = forms.ChoiceField(label=_('Expiration year'), choices=year_choices())
	exp_month = forms.ChoiceField(label=_('Expiration year'), choices=month_choices)
	card_brand = forms.CharField(widget=forms.HiddenInput(), required=False)
	last4 = forms.CharField(widget=forms.HiddenInput(), required=False)

	def adjust_country_field(self):
		countries = Country._default_manager.all()



