from django.urls import reverse_lazy

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.shortcuts import redirect, render, reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_POST

from django.template.loader import render_to_string

from oscar.apps.customer import views
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.compat import get_user_model

from .decorators import persist_basket_contents
from oscar.apps.customer import signals

from dehy.appz.checkout.facade import facade
from dehy.utils import generate_token

EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes('customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm','OrderSearchForm'])
PageTitleMixin = get_class('customer.mixins','PageTitleMixin')
User = get_user_model()

def verify_account(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
		user = None


	if user and generate_token.check_token(user, token):
		user.is_email_verified = True
		user.save()

		messages.success(request, _("Successfully verified account"))
		current_site = get_current_site(request)
		email_subject = _('Account verified!')
		email_body = render_to_string('dehy/customer/partials/account_verification_success_email.html', {
			'user': user,
			'domain': current_site,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': generate_token.make_token(user)
		})
		email = EmailMessage(subject=email_subject, body=email_body,
			from_email=settings.AUTO_REPLY_EMAIL_ADDRESS, to=[user.email])

		email.send()
		return redirect(reverse(settings.OSCAR_ACCOUNTS_REDIRECT_URL))


	return render('dehy/customer/login.html', {'user': user, 'needs_verification': True})



def send_verification_email(user, request):
	if not user.is_email_verified:
		current_site = get_current_site(request)
		email_subject = _('Activate your account')
		email_body = render_to_string('dehy/customer/partials/account_verification_email.html', {
			'user': user,
			'domain': current_site,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': generate_token.make_token(user)
		})
		email = EmailMessage(subject=email_subject, body=email_body,
			from_email=settings.AUTO_REPLY_EMAIL_ADDRESS, to=[user.email])

		email.send()

	messages.info(request, _("An account verification email has been sent to the email address provided, if such an email account exists. Please check your inbox."))



@login_required
@require_POST
def set_card_default(request):
	data = {'badge_text': _('Default payment method'), 'message': _('Failed to set card as default.'), 'button_text': _('Set as default payment method')}
	status_code = 400
	card_id = request.POST.get("card_id", None)
	if card_id:

		customer = facade.stripe.Customer.modify(request.user.stripe_customer_id, default_source=card_id)

		if customer:
			status_code = 200
			data['message'] = _('Updated default payment method!')
			data['card_id'] = customer.default_source


	response = JsonResponse(data)
	response.status_code = status_code
	return response

@login_required
@require_POST
def remove_user_card(request):
	data = {'message': _('Failed to remove card.')}
	status_code = 400
	card_id = request.POST.get("card_id", None)
	if card_id:

		customer = facade.stripe.Customer.delete_source(request.user.stripe_customer_id, card_id)
		if customer:
			status_code = 200
			data['message'] = _('Successfully removed card!')
			data['card_id'] = customer.default_source

	response = JsonResponse(data)
	response.status_code = status_code
	return response


class VerificationView(generic.TemplateView):
	template_name = 'dehy/customer/verification.html'

	# def get(self, request, *args, **kwargs):
	# 	context = self.get_context_data(*args, **kwargs)
	# 	return render(request, self.template_name, context)

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['needs_verification'] = 1
		return context

	def post(self, request, *args, **kwargs):
		email = request.POST.get('username', None)
		if email and User._default_manager.filter(email__iexact=email).exists():
			user = User._default_manager.filter(email__iexact=email).first()
			send_verification_email(user, request)
		else:
			messages.info(self.request, _("An account verification email has been sent to the email address provided, if such an email account exists. Please check your inbox."))

		return redirect(reverse('customer:verification'))


class AccountRegistrationView(views.AccountRegistrationView):
	form_class = EmailUserCreationForm
	template_name = 'dehy/customer/registration.html'


	def post(self, request, *args, **kwargs):
		response = super().post(request, *args, **kwargs)
		return response

	def form_valid(self, form):
		print('form.is_valid(): ', form.is_valid())
		user = self.register_user(form)
		customer = facade.stripe.Customer.create(email=user.email, metadata={'uid':user.id})
		user.stripe_customer_id = customer.id
		user.save()

		send_verification_email(user, self.request)

		messages.success(self.request, _("Successfully created account"), extra_tags='safe noicon')

		return redirect(form.cleaned_data['redirect_url'])

@method_decorator(persist_basket_contents([]), name='dispatch')
class AccountAuthView(views.AccountAuthView, UserPassesTestMixin):
	form_class = EmailAuthenticationForm
	template_name = 'dehy/customer/login.html'
	def test_func(self):
		verified = False
		if hasattr(self.request.user, 'is_email_verified') and self.request.user.is_email_verified:
			verified = True
		return verified

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect(settings.LOGIN_REDIRECT_URL)
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.validate_login_form()

	def validate_login_form(self):
		form = self.get_login_form(bind_data=True)
		if form.is_valid():
			user = form.get_user()

			# Grab a reference to the session ID before logging in
			old_session_key = self.request.session.session_key

			if user.is_email_verified:

				auth_login(self.request, form.get_user())

				# Raise signal robustly (we don't want exceptions to crash the
				# request handling). We use a custom signal as we want to track the
				# session key before calling login (which cycles the session ID).
				signals.user_logged_in.send_robust(
					sender=self, request=self.request, user=user,
					old_session_key=old_session_key)

				msg = self.get_login_success_message(form)
				if msg:
					messages.success(self.request, msg)

				return redirect(self.get_login_success_url(form))

			else:
				messages.error(self.request, _('Email is not verified, please check your email inbox. If you did not receive the verification, resend using the link below'))
				return redirect(reverse('customer:verification'))


		ctx = self.get_context_data(login_form=form)
		return self.render_to_response(ctx)

	# def dispatch(self, *args, **kwargs):
	# 	response = super().dispatch(*args, **kwargs)
	# 	return response

# old
# @method_decorator(persist_basket_contents([]), name='dispatch')
# class AccountAuthView(views.AccountAuthView):
# 	form_class = EmailAuthenticationForm
#
# 	template_name = 'dehy/customer/login.html'
#
# 	def get(self, request, *args, **kwargs):
# 		print('get: ', self.request.GET)
# 		print('request.user.is_authenticated: ', request.user.is_authenticated)
# 		if request.user.is_authenticated:
# 			return redirect(settings.LOGIN_REDIRECT_URL)
# 		return super().get(request, *args, **kwargs)
#
# 	def post(self, request, *args, **kwargs):
# 		print('post: ', self.request.POST)
# 		# Use the name of the submit button to determine which form to validate
# 		if 'login_submit' in request.POST:
# 			return self.validate_login_form()
# 		elif 'registration_submit' in request.POST:
# 			return self.validate_registration_form()
# 		return http.HttpResponseBadRequest()
#
# 	def dispatch(self, *args, **kwargs):
# 		response = super().dispatch(*args, **kwargs)
# 		return response


@method_decorator(persist_basket_contents([]), name='dispatch')
class LogoutView(auth_views.LogoutView):
	redirect_field_name = 'next'

	def dispatch(self, *args, **kwargs):
		response = super().dispatch(*args, **kwargs)
		return response


class ProfileUpdateView(views.ProfileUpdateView):
	active_tab = 'profile-update'


class BillingAddView(PageTitleMixin, TemplateView):
	page_title = _('Billing')
	active_tab = 'billing'
	template_name = "dehy/customer/card_add.html"

class BillingEditView(PageTitleMixin, TemplateView):
	page_title = _('Billing')
	active_tab = 'billing'
	template_name = "dehy/customer/card_edit.html"


class BillingListView(PageTitleMixin, TemplateView):
	page_title = _('Billing')
	active_tab = 'billing'
	template_name = "dehy/customer/card_list.html"

	def post(self, request, *args, **kwargs):
		pass

	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)
		customer = facade.stripe.Customer.retrieve(self.request.user.stripe_customer_id)

		cards = facade.stripe.Customer.list_sources(
			self.request.user.stripe_customer_id,
			object="card", limit=10
		)

		context_data['cards'] = []
		for card in cards['data']:
			is_default = True if card['id']==customer.default_source else False

			_card = {
				'name': card['name'],
				'billing_address': {
					'line1': card['address_line1'],
					'line4': card['address_city'],
					'state': card['address_state'],
					'postcode': card['address_zip'],
					'country': card['address_country'],
				},
				'last4': card['last4'],
				'exp_month': card['exp_month'],
				'exp_year': card['exp_year'],
				'brand': card['brand'],
				'is_default': is_default,
				'id': card['id']
			}

			if card['address_line2']:
				_card['line2'] = card['address_line2']

			_card['billing_address'] = {k: v for k, v in _card['billing_address'].items() if v}
			_card = {k: v for k, v in _card.items() if v}

			context_data['cards'].append(_card)

		# context_data.update({'payment_methods': payment_methods})
		return context_data

