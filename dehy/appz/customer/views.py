from django.views import generic
from oscar.apps.customer import views
from oscar.core.loading import get_class, get_classes, get_model, get_profile_class

EmailAuthenticationForm, EmailUserCreationForm, OrderSearchForm = get_classes('customer.forms', ['EmailAuthenticationForm', 'EmailUserCreationForm','OrderSearchForm'])

class AccountAuthView(views.AccountAuthView):
	form_class = EmailAuthenticationForm