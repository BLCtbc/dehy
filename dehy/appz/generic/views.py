from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from .models import QandA

class CustomView(TemplateView):
	template_name = "dehy/custom.html"

class WholesaleView(TemplateView):
	template_name = "dehy/wholesale.html"

class HomeView(TemplateView):
	template_name = "dehy/home.html"

class ReturnsRefundsView(TemplateView):
	template_name = "dehy/returns.html"

class ContactView(TemplateView):
	template_name = "dehy/contact.html"

class FAQView(ListView):
	model = QandA
	template_name = "dehy/faq.html"


def get_cart_quantity(request):
	status_code = 200
	cart = request.basket
	data = {'num_cart_items': cart.num_items}
	response = JsonResponse(data, safe=False)
	response.status_code = status_code

	return response