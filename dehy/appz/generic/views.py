from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from oscar.core.loading import get_class, get_model

FAQ = get_model('generic', 'FAQ')
Product = get_model('catalogue', 'Product')
Recipe = get_model('recipes', 'Recipe')

class CustomView(TemplateView):
	template_name = "dehy/custom.html"

class WholesaleView(TemplateView):
	template_name = "dehy/wholesale.html"


class PrivacyPolicyView(TemplateView):
	template_name = "dehy/privacy_policy.html"

class TermsOfServiceView(TemplateView):
	template_name = "dehy/terms_of_service.html"

class HomeView(TemplateView):
	template_name = "dehy/home.html"

	def get_context_data(self, *args, **kwargs):
		data = super().get_context_data(*args, **kwargs)
		recipes = Recipe.objects.filter(featured=True)
		products = Product.objects.exclude(product_class__name='Merch', structure='child')
		data.update({'recipes':recipes, 'products':products})
		return data

class ReturnsRefundsView(TemplateView):
	template_name = "dehy/returns.html"

class ContactView(TemplateView):
	template_name = "dehy/contact.html"

class FAQView(ListView):
	model = FAQ
	context_object_name = "faq_list"
	template_name = "dehy/faq.html"


def get_cart_quantity(request):
	status_code = 200
	cart = request.basket
	data = {'num_cart_items': cart.num_items}
	response = JsonResponse(data, safe=False)
	response.status_code = status_code

	return response