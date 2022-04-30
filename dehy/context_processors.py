from django.contrib.auth import models
from oscar.core.loading import get_class
from oscar.core import prices

BasketLineFormSet = get_class('basket.formsets', 'BasketLineFormSet')

def add_ig_images_to_context(request):
	context = {'ig_images': ['CMl2W97MQzf', 'CMpOpoxrMJz', 'CMxItVrHf9_', 'COaaOwEl_Cu', 'CNVDJAgjq3e', 'CM8IQsolNQD']}
	return context

def order_total(request):
	excl_tax = request.basket.total_excl_tax
	incl_tax = request.basket.total_incl_tax if request.basket.is_tax_known else None
	return {'order_total': prices.Price(currency=request.basket.currency, excl_tax=excl_tax, incl_tax=incl_tax)}


def basket_contents(request):
	return {'basket_formset':BasketLineFormSet(queryset=request.basket.all_lines(), strategy=request.basket.strategy)}