from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, ModelFormMixin, ProcessFormView
from django.views.generic.base import RedirectView
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from oscar.core.compat import get_user_model
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import LoginRequiredMixin

from pathlib import Path

from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model

from dehy.appz.checkout import facade
from dehy.appz.generic import forms

import json, logging, os, requests
from dehy.appz.generic.models import Message, MessageUser

FAQ = get_model('generic', 'FAQ')
Product = get_model('catalogue', 'Product')
Recipe = get_model('recipes', 'Recipe')
Order = get_model('order', 'Order')
User = get_user_model()

ShippingAddressForm = get_class('checkout.forms', 'ShippingAddressForm')
ShippingAddress = get_model('order', 'ShippingAddress')
Repository = get_class('shipping.repository', 'Repository')
Repository = Repository()
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('__name__')
logging.debug('generic views file')


@csrf_exempt
def shipstation_webhook_order_shipped(request):
	body,data = request.body,''
	if type(body) == bytes:
		data = body.decode()

	if type(data) == str:
		data = json.loads(body)

	resource_url = data.get('resource_url', None)
	if resource_url:
		headers = Repository.shipstation_get_headers()
		response = requests.get(resource_url, headers=headers)

		if status_code != 200:
			error_msg = f"{status_code} - A problem occurred while retrieving shipstation webhook"

		else:
			response_list = json.loads(response.text)
			for item in response_list['shipments']:
				shipstation_order_id = item['orderNumber']
				order_id = int(shipstation_order_id) - 10000
				order = Order.objects.filter(id=order_id)
				if order:
					order = order.first()
					order.status = 'Shipped'
					order.save()

@csrf_exempt
def shipstation_webhook_order_received(request):

	# try:
	body,data = request.body,''
	msg = f'body: {body}'
	logger.debug('logger: '+msg)
	logging.debug('logging: '+msg)
	if type(body) == bytes:
		data = body.decode()

	if type(data) == str:
		data = json.loads(body)

	logger.debug(f'request.body: {request.body}')

	logging.debug(f'shipstation webhook POST: {request.POST}')
	logger.debug(f'shipstation webhook POST: {request.POST}')
	resource_url = data.get('resource_url', None)

	if resource_url:
		headers = Repository.shipstation_get_headers()
		response = requests.get(resource_url, headers=headers)
		msg = f'response: {response}'
		status_code = response.status_code
		# request was good, create the methods
		if status_code != 200:
			error_msg = f"{status_code} - A problem occurred while retrieving shipstation webhook"
			logger.error(error_msg)

		else:
			response_list = json.loads(response.text)
			for item in response_list['orders']:
				msg = f"orderId: {item['orderId']}, orderNumber: {item['orderNumber']}, orderKey: {item['orderKey']}"

				shipstation_order_id = item['orderNumber']
				order_id = int(shipstation_order_id) - 10000

				order = Order.objects.filter(id=order_id)
				if order:
					order = order.first()
					order.set_status('Processed')

					current_site = get_current_site(request)
					email_subject = f"DEHY: A New Order has Arrived ({order.number})"
					email_body = render_to_string('oscar/communication/emails/internal/order_received.txt', {
						'order': order,
						'ship_by': item['shipByDate'],
						'site': current_site
					})

					email_body_html = render_to_string('oscar/communication/emails/internal/order_received.html', {
						'order': order,
						'ship_by': item['shipByDate'],
						'site': current_site
					})


					recipients = list(user.email for user in User.objects.filter(receive_new_order_notifications=True))
					recipients += [f'orders@{current_site}']
					logger.debug(f'recipients: {recipients}')

					sent = send_mail(email_subject, email_body, settings.AUTO_REPLY_EMAIL_ADDRESS, recipients, fail_silently=False, html_message=email_body_html)

	response = HttpResponse("Testing order received webhook")
	return response

	#
	# except Exception as e:
	# 	error_msg = f"Error retrieving shipstation webhook: {e}"
	# 	print(error_msg)
	# 	logger.debug(error_msg)
	# 	logger.error(error_msg)


def get_validated_address(request):
	data = {}
	status_code = 200
	shipping_form = ShippingAddressForm(request.POST)

	address_fields = dict((k, v) for (k, v) in shipping_address_form.instance.__dict__.items() if not k.startswith('_'))
	phone_number = address_fields.get('phone_number').as_international if address_fields.get('phone_number', None) else None
	if phone_number:
		address_fields.update({'phone':phone_number})

	shipping_address = ShippingAddress(**address_fields)
	data['address'] = Repository.validate_address(shipping_address)

	response = JsonResponse(data)
	response.status_code = status_code
	return response



def recaptcha_verify(request):
	print('\n attempting to verify recaptcha')
	data = {}
	status_code = 400
	url = "https://www.google.com/recaptcha/api/siteverify"
	token = request.GET.get('token', None)
	if token:
		secret_key = settings.GOOGLE_RECAPTCHA_V2_SECRET_KEY
		if request.GET.get('version', '') == 3:
			secret_key = settings.GOOGLE_RECAPTCHA_V3_SECRET_KEY

		status_code = 200

		payload = {
			'response': token,
			'secret': secret_key
		}

		remote_ip = request.META.get('REMOTE_ADDR')
		remote_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))

		if remote_ip:
			remote_ip = remote_ip.split(',')[0].strip()
			payload.update({'remoteip': remote_ip})

		recaptcha_response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)

		data.update(json.loads(recaptcha_response.text))


	response = JsonResponse(data)
	response.status_code = status_code
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
			request.session['notifications'] = message

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

class InvoiceView(LoginRequiredMixin, DetailView):
	login_url = reverse_lazy('customer:login')
	redirect_field_name = 'next'
	model = Order
	template_name = "dehy/generic/invoice.html"

	def get_object(self, queryset=None):
		object = super().get_object(queryset)
		print('object: ', object)
		print(object.user and object.user == self.request.user)
		if self.request.user.is_superuser or self.request.user.is_superuser or (object.user and object.user == self.request.user):
			return object

class PrivacyPolicyView(TemplateView):
	template_name = "dehy/generic/privacy_policy.html"

class TermsOfServiceView(TemplateView):
	template_name = "dehy/generic/terms_of_service.html"

class HomeView(TemplateView):
	template_name = "dehy/generic/home.html"

	def get_context_data(self, *args, **kwargs):
		data = super().get_context_data(*args, **kwargs)
		recipes = Recipe.objects.filter(featured=True)
		products = Product._default_manager.filter(featured=True).exclude(product_class__name='Merch', structure='child')

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
			request.session['notifications'] = _('Successfully sent message!')
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