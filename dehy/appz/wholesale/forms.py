from django import forms
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from dehy.appz.generic.models import Message, MessageUser
from oscar.forms.mixins import PhoneNumberMixin
from oscar.core.loading import get_class, get_model
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site

from phonenumber_field.formfields import PhoneNumberField
# from phonenumber_field.phonenumber import PhoneNumber
import datetime

Country = get_model('address', 'Country')

class WholesaleAccountCreationForm(PhoneNumberMixin, forms.Form):

	product_interest_choices = (
		("lemon", "Lemon"),
		("lime", "Lime"),
		("orange", "Orange"),
		("blood_orange", "Blood Orange"),
		("grapefruit", "Grapefruit"),
		("pineapple", "Pineapple"),
		("dragon_fruit", "Dragon Fruit"),
		("kiwi", "Kiwi"),
		("star_fruit", "Star Fruit"),
		("lotus_root", "Lotus Root"),
		("apple", "Apple"),
		("pear", "Pear"),
		("figs", "Figs"),
		("spray_roses", "Spray Roses"),
		("cushion_pom_flowers", "Cushion Pom Flowers"),
		("thick_cut_citrus", "Thick Cut Citrus"),
		("custom_garnishes", "Custom Garnishes"),
	)

	organization_choices = (
		('bar', 'Bar'),
		('restaurant', 'Restaurant'),
		('hotel_resort', 'Hotel / Resort'),
		('mobile_bar_catering', 'Mobile Bar / Catering'),
		('restaurant_group', 'Restaurant Group'),
		('retailer', 'Retailer'),
		('other', 'Other'),
	)

	phone_number_fields = {
        'phone_number': {
            'required': True,
            'help_text': '',
            'max_length': 32,
            'label': _('Phone number')
        },
		'billing_phone_number': {
            'required': True,
            'help_text': '',
            'max_length': 32,
            'label': _('Billing Phone number')
        },
    }
	company_name = forms.CharField(required=True, label=_('Company Name'))
	organization = forms.ChoiceField(label=_('Type of Organization'), required=True, choices=organization_choices)
	first_name = forms.CharField(required=True, label=_('First Name'))
	last_name = forms.CharField(required=True, label=_('Last Name'))
	position = forms.CharField(required=True, label=_('Position'))
	phone_number = PhoneNumberField(required=True, max_length=32, label=('Phone Number'))
	email = forms.EmailField(required=True, label=_("Email"))
	billing_first_name = forms.CharField(required=True, label=_('First Name'))
	billing_last_name = forms.CharField(required=True, label=_('Last Name'))
	billing_phone_number = PhoneNumberField(required=True, max_length=32, label=('Billing Phone Number'))

	billing_email = forms.EmailField(required=True, label=_("Billing Email"))
	billing_line1 = forms.CharField(required=True, label=_('Address 1'))
	billing_line2 = forms.CharField(required=False, label=_('Address 2'))
	billing_line4 = forms.CharField(required=True, label=_("City"))
	billing_state = forms.CharField(required=True, label=_("State"))
	billing_country = forms.CharField(required=True, label=_("Country"))
	billing_postcode = forms.CharField(required=True, label=_("Zip/Postal Code"))

	shipping_line1 = forms.CharField(required=True, label=_('Address 1'))
	shipping_line2 = forms.CharField(required=False, label=_('Address 2'))
	shipping_line4 = forms.CharField(required=True, label=_("City"))
	shipping_state = forms.CharField(required=True, label=_("State"))
	shipping_country = forms.CharField(required=True, label=_("Country"))
	shipping_postcode = forms.CharField(required=True, label=_("Zip/Postal Code"))
	shipping_notes = forms.CharField(required=False, label=_('Shipping / Delivery Instructions'), help_text=_("For local delivery, include delivery windows and days"), widget=forms.Textarea(attrs={'cols': 30, 'rows': 4}))
	product_interests = forms.MultipleChoiceField(label=_("Which dehydrated garnishes are you interested in?"), widget=forms.CheckboxSelectMultiple, choices=product_interest_choices)

	class Meta:
		fields = [
			'company_name', 'organization', 'position', 'first_name', 'last_name',
			'phone_number', 'email', 'billing_first_name', 'billing_last_name',
			'billing_phone_number', 'billing_line1', 'billing_line2', 'billing_line4',
			'billing_state', 'billing_postcode', 'billing_country',
			'shipping_line1', 'shipping_line2', 'shipping_line4',
			'shipping_state', 'shipping_postcode', 'shipping_country', 'shipping_notes', 'product_interests'
		]

	def adjust_country_field(self):
		countries = Country._default_manager.filter(Q(iso_3166_1_a2='US')|Q(iso_3166_1_a2='CA'))

		# No need to show country dropdown if there is only one option
		if len(countries) == 1:
			self.fields.pop('billing_country', None)
			self.instance.billing_country = countries[0]

			self.fields.pop('shipping_country', None)
			self.instance.shipping_country = countries[0]
		else:
			self.fields['billing_country'].queryset = countries
			self.fields['billing_country'].empty_label = None
			self.fields['shipping_country'].queryset = countries
			self.fields['shipping_country'].empty_label = None

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self.country = self.get_country()
		self.adjust_country_field()

		self.fields['position'].widget.attrs.update({'placeholder': _('Bar Manager, Beverage Director, etc.')})

	def get_country(self):
		return Country.objects.get(iso_3166_1_a2='US')

	def send_email(self, request):

		for field in self.fields:
			self.fields[field].widget.attrs.update({'readonly': True, 'disabled': True})

		current_site = get_current_site(request)
		recipients = [f'info@{current_site}']

		email_subject = 'DEHY: Wholesale Account Creation Request'

		email_body = render_to_string('dehy/wholesale/partials/account_creation_email.html', {
			'form': self,
		})

		email_body_html = render_to_string('dehy/wholesale/partials/account_creation_email.html', {
			'form': self,
		})

		try:
			sent = send_mail(email_subject, email_body, from_email=settings.AUTO_REPLY_EMAIL_ADDRESS, recipient_list=recipients, fail_silently=False, html_message=email_body_html)
			request.session['notifications'] = str(_('Account creation request sent!'))
			messages.success(request, str(_('Account creation request sent!')))

		except Exception as e:
			error_msg =  str(_('Uh oh! A problem occurred while sending your account creation request email. Please try again later'))
			request.session['notifications'] = error_msg
			messages.error(self.request, error_msg)

	def create_customer(self):
		cleaned_data = self.cleaned_data
		payload = {
			"Customer": {
				"GivenName": cleaned_data['first_name'],
				"FamilyName": cleaned_data['last_name'],

				"PrimaryEmailAddr": {
					"Address": cleaned_data['email']
				},
				"Mobile": {
					"FreeFormNumber": cleaned_data['phone_number']
				},
				"ShipAddr": {
					"PostalCode": cleaned_data['shipping_postcode'],
					"City": cleaned_data['shipping_line4'],
					"Country": cleaned_data['shipping_country'],
					"Line1": cleaned_data["shipping_line1"],
					"Line2": cleaned_data["shipping_line2"],
					"CountrySubDivisionCode": cleaned_data['shipping_state'],
					"Id": "3"
				},
				"CompanyName": cleaned_data["company_name"],
				"Active": True,
				"BillAddr": {
					"PostalCode": cleaned_data['billing_postcode'],
					"City": cleaned_data['billing_line4'],
					"Country": cleaned_data['billing_country'],
					"Line1": cleaned_data["billing_line1"],
					"Line2": cleaned_data["billing_line2"],
					"CountrySubDivisionCode": cleaned_data['billing_state'],
					"Id": "3"
				},
				"Notes": f"Position: {cleaned_data['position']}, Product Interests: {cleaned_data['product_interests']}"
			}
		}

		response = quickbooks.api_call('customer', payload)