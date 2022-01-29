from django.views.generic import TemplateView

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

