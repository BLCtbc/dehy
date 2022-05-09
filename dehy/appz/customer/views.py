from django.urls import reverse_lazy
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import generic

from oscar.apps.customer import views
from oscar.core.loading import get_class, get_classes, get_model

from .decorators import persist_basket_contents
from dehy.appz.checkout.facade import Facade
Facade = Facade()


PageTitleMixin = get_class('customer.mixins','PageTitleMixin')

EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes('customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm','OrderSearchForm'])


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
		print('session items(auth view): ', self.request.session.items())
		print('dispatch1 (auth view): ', self.request.basket)
		response = super().dispatch(*args, **kwargs)
		print('dispatch2 (auth view): ', self.request.basket)
		return response

# class LogoutView(generic.RedirectView):
# 	url = settings.OSCAR_HOMEPAGE
# 	permanent = False
# 	redirect_field_name = 'next'
#
# 	# def dispatch(self, *args, **kwargs):
# 	# 	print('dispatching')
# 	# 	print('basket1(dispatch): ', self.request.basket)
# 	# 	response = super().dispatch(*args, **kwargs)
# 	# 	print('basket2(dispatch): ', self.request.basket)
# 	#
# 	# 	return response
#
#
# 	def get(self, request, *args, **kwargs):
# 		print('get1: ', request.basket)
#
# 		auth_logout(request)
# 		print('get2: ', request.basket)
#
# 		response = super().get(request, *args, **kwargs)
#
# 		for cookie in settings.OSCAR_COOKIES_DELETE_ON_LOGOUT:
# 			response.delete_cookie(cookie)
#
# 		print('get3: ', request.basket)
#
# 		return response

@method_decorator(persist_basket_contents([]), name='dispatch')
class LogoutView(auth_views.LogoutView):
	redirect_field_name = 'next'

	# def setup(self, request, *args, **kwargs):
	# 	print('setup')
	# 	print('basket1(setup): ', request.basket)
	# 	response = super().setup(request, *args, **kwargs)
	# 	print('basket2(setup): ', request.basket)
	# 	return response

	def dispatch(self, *args, **kwargs):
		print('logging out')
		print('dispatch1: ', self.request.basket)
		response = super().dispatch(*args, **kwargs)
		print('dispatch2: ', self.request.basket)

		return response


class ProfileUpdateView(views.ProfileUpdateView):
	active_tab = 'profile-update'

#
class BillingInfoView(PageTitleMixin, generic.FormView):


	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)

		payment_methods = Facade.stripe.PaymentMethod.list(
			customer=request.user.stripe_customer_id,
			type="card",
		)

		context_data.update({'payment_methods': payment_methods})
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