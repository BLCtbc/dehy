from django.urls import reverse_lazy
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import views as auth_views
from django.http import JsonResponse

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from django.views import generic
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from oscar.apps.customer import views
from oscar.core.loading import get_class, get_classes, get_model

from .decorators import persist_basket_contents
from dehy.appz.checkout.facade import Facade
Facade = Facade()


PageTitleMixin = get_class('customer.mixins','PageTitleMixin')

EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes('customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm','OrderSearchForm'])

@login_required
@require_POST
def set_card_default(request):
	data = {'badge_text': _('Default payment method'), 'message': _('Failed to set card as default.'), 'button_text': _('Set as default payment method')}
	status_code = 400
	card_id = request.POST.get("card_id", None)
	if card_id:

		customer = Facade.stripe.Customer.modify(request.user.stripe_customer_id, default_source=card_id)

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
	data = {'message': _('Failed remove card.')}
	status_code = 400
	card_id = request.POST.get("card_id", None)
	if card_id:

		customer = Facade.stripe.Customer.delete_source(request.user.stripe_customer_id, card_id)
		if customer:
			status_code = 200
			data['message'] = _('Successfully removed card!')
			data['card_id'] = customer.default_source


	response = JsonResponse(data)
	response.status_code = status_code
	return response

class AccountRegistrationView(views.AccountRegistrationView):
	form_class = EmailUserCreationForm
	template_name = 'dehy/customer/registration.html'

	def post(self, request, *args, **kwargs):

		print('\npost: ', request.POST)
		response = super().post(request, *args, **kwargs)

		return response

	def form_valid(self, form):
		user = self.register_user(form)
		print('created user: ', user)
		customer = Facade.stripe.Customer.create(email=user.email, metadata={'uid':user.id})
		user.stripe_customer_id = customer.id
		user.save()

		return redirect(form.cleaned_data['redirect_url'])

@method_decorator(persist_basket_contents([]), name='dispatch')
class AccountAuthView(views.AccountAuthView):
	form_class = EmailAuthenticationForm
	template_name = 'dehy/customer/login.html'

	def dispatch(self, *args, **kwargs):
		response = super().dispatch(*args, **kwargs)
		return response


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

#
class BillingListView(PageTitleMixin, TemplateView):
	page_title = _('Billing')
	active_tab = 'billing'
	template_name = "dehy/customer/card_list.html"

	def post(self, request, *args, **kwargs):
		pass

	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)

		# payment_methods = Facade.stripe.PaymentMethod.list(
		# 	customer=self.request.user.stripe_customer_id,
		# 	type="card"
		# )
		customer = Facade.stripe.Customer.retrieve(self.request.user.stripe_customer_id)
		print('customer: ', customer)

		cards = Facade.stripe.Customer.list_sources(
			self.request.user.stripe_customer_id,
			object="card", limit=10
		)
		print('cards: ', cards)

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

			print('adding card: ', _card)
			context_data['cards'].append(_card)

		# context_data.update({'payment_methods': payment_methods})
		return context_data

	# def get(self, request, *args, **kwargs):
	# 	response = super().get(request, *args, **kwargs)
	#


	# permanent = False
	# # query_string = True
	# # url = '/'
	#
	# def get(self, request, *args, **kwargs):
	# 	print('dir(self): ', dir(self))
	# 	print('dir(request): ', dir(request))
	# 	print('session: ', request.session)
	# 	print('dir(session): ', dir(request.session))
	#
	# 	auth_logout(request)
	# 	response = super().get(request, *args, **kwargs)
	# 	next = self.request.GET.get('next')
	# 	print('next: ', next)
	# 	for cookie in settings.OSCAR_COOKIES_DELETE_ON_LOGOUT:
	# 		response.delete_cookie(cookie)
	#
	#
	# 	return response

# class LogoutView(views.LogoutView):
# 	url = reverse_lazy('customer:login')
# 	query_string = True
#
# 	def get(self, request, *args, **kwargs):
#
# 		response = super().get(request, *args, **kwargs)
# 		print('dir(self): ', dir(self))
# 		print('self.url: ', self.url)
# 		print('dir(request): ', dir(request))
#
# 		return response