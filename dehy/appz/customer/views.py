from django.views import generic
from oscar.apps.customer import views
from oscar.core.loading import get_class, get_classes, get_model
from django.urls import reverse_lazy

EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes('customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm','OrderSearchForm'])


class AccountRegistrationView(views.AccountRegistrationView):
	form_class = EmailUserCreationForm
	template_name = 'dehy/customer/registration.html'

class AccountAuthView(views.AccountAuthView):
	form_class = EmailAuthenticationForm
	template_name = 'dehy/customer/login.html'

class LogoutView(views.LogoutView):
	url = reverse_lazy('customer:login')
