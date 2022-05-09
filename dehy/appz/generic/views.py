from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView, ModelFormMixin, ProcessFormView
from django.views.generic.base import RedirectView
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _

from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site

from pathlib import Path

from oscar.core.loading import get_class, get_model

from dehy.appz.checkout import facade
from dehy.appz.generic import forms

import json, os, requests
from dehy.appz.generic.models import Message, MessageUser

FAQ = get_model('generic', 'FAQ')
Product = get_model('catalogue', 'Product')
Recipe = get_model('recipes', 'Recipe')

def recaptcha_verify(request):
	print('\n attempting to verify recaptcha')

	url = "https://www.google.com/recaptcha/api/siteverify"
	payload = {
		'secret': settings.GOOGLE_RECAPTCHA_V3_SECRET_KEY,
		'response': request.GET.get('token'),
	}
	req = requests.request("POST", url, data=json.dumps(payload))
	print('\n recaptcha: ', req)

	data = {}
	response = JsonResponse(data)
	return response


class MailingListView(ModelFormMixin, ProcessFormView):
	success_url = reverse_lazy('home')
	form_class = forms.MailingListUserForm
	model = MessageUser
	def post(self, request, *args, **kwargs):

		status_code = 400
		message = _('Uh oh, something went wrong...')
		data = {}

		form = self.form_class(self.request.POST)
		if form.is_valid() and self.form_valid(form):
			status_code = 200
			message = _("Successfully added email to mailing list: ")
			message += form.cleaned_data["email"]
		else:

			for k,v in form.errors.as_data().items():
				message += ' '.join(v[0])

		data['status_code'] = status_code
		data['message'] = message

		response = JsonResponse(data)
		response.status_code = status_code

		return response


@require_POST
def mailing_list(request):
	pass

def contact_view(request):
	url = request._current_scheme_host+reverse_lazy('faq')+"#contact"
	request.status_code = 302
	return redirect(url)
	# pattern_name = 'faq'

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
		products = Product._default_manager.exclude(product_class__name='Merch', structure='child')

		data.update({'recipes':recipes, 'products':products, 'mailing_list_form': forms.MailingListUserForm})
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
		current_site = settings.SITE_DOMAIN
		contact_form = self.form_class(request.POST)
		if contact_form.is_valid():
			first_name = contact_form.cleaned_data.get('first_name', None)
			last_name = contact_form.cleaned_data.get('last_name', None)
			email = contact_form.cleaned_data.get('email', None)

			subject = contact_form.cleaned_data.get('subject', None)
			message = contact_form.cleaned_data.get('message', None)
			recipients = [f'faq+contact@{current_site}']
			subject = f'[CONTACT FORM] FROM: {email} SUBJECT: {subject}'
			sent = send_mail(subject, message, settings.OSCAR_FROM_EMAIL, recipients, fail_silently=False)
			print('emails sent: ', sent)
			response = redirect(self.success_url)
			return response

			# some kind of rate limiting/spam detection, etc. would be good here
			# maybe a captcha?
			# email_user = MessageUser.objects.get_or_create()

			# if 'email' in contact_form.cleaned_data:
				# new_message = contact_form.save(commit=False)
				# message_user = forms.MessageUserForm(self.cleaned_data['email'])

				# if message_user.is_valid():
					# message_user.save()
					# new_message.email = message_user.instance.address
					# new_message.save()




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