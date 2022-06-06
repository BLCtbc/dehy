from django.contrib.auth import models
from oscar.core.loading import get_class
from oscar.core import prices
from django.conf import settings

BasketLineFormSet = get_class('basket.formsets', 'BasketLineFormSet')
Applicator = get_class('offer.applicator', 'Applicator')

def add_ig_images_to_context(request):
	context = {'ig_images': ['CMl2W97MQzf', 'CMpOpoxrMJz', 'CMxItVrHf9_', 'COaaOwEl_Cu', 'CNVDJAgjq3e', 'CM8IQsolNQD']}
	return context

def order_total(request):
	excl_tax = request.basket.total_excl_tax
	incl_tax = request.basket.total_incl_tax if request.basket.is_tax_known else None
	return {'order_total': prices.Price(currency=request.basket.currency, excl_tax=excl_tax, incl_tax=incl_tax)}

def add_upsell_messages(request):
	offers = Applicator().get_offers(request.basket, request.user, request)
	applied_offers = list(request.basket.offer_applications.offers.values())
	msgs = []
	for offer in offers:
		if offer.is_condition_partially_satisfied(request.basket) and offer not in applied_offers:
			data = {'message': offer.get_upsell_message(request.basket),'offer': offer}
			msgs.append(data)
	return {'upsell_messages': msgs}

def basket_contents(request):
	return {'basket_formset':BasketLineFormSet(queryset=request.basket.all_lines(), strategy=request.basket.strategy)}

def add_recaptcha_site_keys(request):
	return {'recaptcha_site_key_v2': settings.GOOGLE_RECAPTCHA_V2_SITE_KEY, 'recaptcha_site_key_v3': settings.GOOGLE_RECAPTCHA_V3_SITE_KEY}

def add_notifications(request):
	notifications = request.session.get('notifications', None)
	if notifications:

		request.session.pop('notifications')
		return {'notifications': notifications}

	return {'notifications':""}