from django import forms

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from oscar.apps.customer.forms import EmailAuthenticationForm as BaseEmailAuthenticationForm
from oscar.apps.customer.forms import EmailUserCreationForm as BaseEmailUserCreationForm

class EmailAuthenticationForm(BaseEmailAuthenticationForm):
	username = forms.EmailField(label=_('Email'))

class EmailUserCreationForm(BaseEmailUserCreationForm):

	first_name = forms.CharField(label=_('First Name'), required=True)
	last_name = forms.CharField(label=_('Last Name'), required=True)
	email = forms.EmailField(label=_('Email'))
	field_order = ['first_name', 'last_name', 'email', 'password1', 'password2']


