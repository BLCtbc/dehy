from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse_lazy

from pathlib import Path

from oscar.core.loading import get_class, get_model

from dehy.appz.checkout import facade
from dehy.appz.generic import forms

import os

FAQ = get_model('generic', 'FAQ')
Product = get_model('catalogue', 'Product')
Recipe = get_model('recipes', 'Recipe')

class WholesaleView(TemplateView):
	template_name = "dehy/generic/wholesale.html"

class PrivacyPolicyView(TemplateView):
	template_name = "dehy/generic/privacy_policy.html"

class TermsOfServiceView(TemplateView):
	template_name = "dehy/generic/terms_of_service.html"

class HomeView(TemplateView):
	template_name = "dehy/generic/home.html"

	def get_context_data(self, *args, **kwargs):
		data = super().get_context_data(*args, **kwargs)
		recipes = Recipe.objects.filter(featured=True)
		products = Product.objects.exclude(product_class__name='Merch', structure='child')
		data.update({'recipes':recipes, 'products':products})
		return data

class ReturnsRefundsView(TemplateView):
	template_name = "dehy/generic/returns.html"

class FAQView(ListView, FormView):
	model = FAQ
	form_class = forms.ContactForm
	context_object_name = "faq_list"
	template_name = "dehy/generic/faq.html"
	success_url = reverse_lazy('catalogue:index')

	def get_context_data(self, *args, **kwargs):

		context_data = super().get_context_data(*args, **kwargs)
		faq_image_folder = Path(settings.BASE_DIR) / 'media/images/faq/'
		image_list = os.listdir(faq_image_folder)
		context_data.update({'image_list': image_list})
		return context_data


	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			email_user = MessageUser.objects.get_or_create()
			form.send_email()

			# add some kind of rate limiting here

	#
	# def form_valid(self, form):
	# 	form.send_email()
	# 	return super().form_valid(form)


@method_decorator(csrf_exempt)
def create_checkout_session(request):
	session = facade.Facade().session()
	return redirect(session.url, code=303)

def get_cart_quantity(request):
	status_code = 200
	cart = request.basket
	data = {'basket_items': cart.num_items}
	response = JsonResponse(data, safe=False)
	response.status_code = status_code

	return response