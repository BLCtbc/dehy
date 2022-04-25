from django.views import generic
from oscar.apps.customer import views
from oscar.core.loading import get_class, get_classes, get_model
from django.urls import reverse_lazy
from django.contrib.auth import logout as auth_logout
from django.conf import settings

from django.contrib.auth import views as auth_views


EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes('customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm','OrderSearchForm'])


class AccountRegistrationView(views.AccountRegistrationView):
	form_class = EmailUserCreationForm
	template_name = 'dehy/customer/registration.html'

class AccountAuthView(views.AccountAuthView):
	form_class = EmailAuthenticationForm
	template_name = 'dehy/customer/login.html'


class LogoutView(auth_views.LogoutView):
	redirect_field_name = 'next'

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