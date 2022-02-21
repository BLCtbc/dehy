from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from oscar.core.loading import get_class, get_model
from dehy.appz.checkout import facade
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dehy.appz.generic import forms

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

class ContactView(TemplateView):
	template_name = "dehy/generic/contact.html"
	form_class = forms.ContactForm

	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)
		context_data['contact_form'] = kwargs.get('contact_form', self.form_class)
		return context_data

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			pass

			# email_user = MessageUser.objects.get_or_create()
			# add some kind of rate limiting here

class FAQView(ListView):
	model = FAQ
	context_object_name = "faq_list"
	template_name = "dehy/generic/faq.html"

@method_decorator(csrf_exempt)
def create_checkout_session(request):
	session = facade.Facade().session()
	return redirect(session.url, code=303)

def get_cart_quantity(request):
	status_code = 200
	cart = request.basket
	data = {'num_cart_items': cart.num_items}
	response = JsonResponse(data, safe=False)
	response.status_code = status_code

	return response