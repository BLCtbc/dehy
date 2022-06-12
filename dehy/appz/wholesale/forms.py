from django import forms
from django.utils.translation import gettext_lazy as _
from dehy.appz.generic.models import Message, MessageUser
from oscar.forms.mixins import PhoneNumberMixin
from oscar.core.loading import get_class, get_model
from django.db.models import Q

Country = get_model('address', 'Country')

class WholesaleAccountCreationForm(forms.Form, PhoneNumberMixin):
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
	phone_number_fields = {
        'phone_number': {
            'required': True,
            'help_text': '',
            'max_length': 32,
            'label': _('Phone Number')
        },
		'billing_phone_number': {
            'required': True,
            'help_text': '',
            'max_length': 32,
            'label': _('Billing Phone Number')
        },
    }
	organization_choices = (
		('bar', 'Bar'),
		('restaurant', 'Restaurant'),
		('hotel_resort', 'Hotel / Resort'),
		('mobile_bar_catering', 'Mobile Bar / Catering'),
		('restaurant_group', 'Restaurant Group'),
		('retailer', 'Retailer'),
		('other', 'Other'),

	)
	email = forms.EmailField(required=True, label=_("Email"))
	company_name = forms.CharField(required=True, label=_('Company Name'))
	organization = forms.ChoiceField(label=_('Type of Organization'), required=True, choices=organization_choices)
	position = forms.CharField(required=True, label=_('Position'))
	first_name = forms.CharField(required=True, label=_('First Name'))
	last_name = forms.CharField(required=True, label=_('Last Name'))
	billing_first_name = forms.CharField(required=True, label=_('First Name'))
	billing_last_name = forms.CharField(required=True, label=_('Last Name'))
	billing_email = forms.EmailField(required=True, label=_("Email"))
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
			'first_name', 'last_name',
            'billing_first_name', 'billing_last_name',
            'billing_line1', 'billing_line2', 'billing_line4',
            'billing_state', 'billing_postcode', 'billing_country',
            'phone_number', 'shipping_notes', 'billing_phone_number',
            'shipping_line1', 'shipping_line2', 'shipping_line4',
            'shipping_state', 'shipping_postcode', 'shipping_country','product_interests'
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
		print('self.fields: ', self.fields)
		self.adjust_country_field()

		self.fields['position'].widget.attrs.update({'placeholder': _('Bar Manager, Beverage Director, etc.')})
