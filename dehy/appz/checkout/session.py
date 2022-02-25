
from oscar.apps.checkout import session
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from oscar.apps.checkout import exceptions

class CheckoutSessionMixin(session.CheckoutSessionMixin):
	def check_user_email_is_captured(self, request):
		if not request.user.is_authenticated \
				and not self.checkout_session.get_guest_email():
			raise exceptions.FailedPreCondition(
				url=reverse('checkout:index'),
				message=_(
					"Please either sign in or enter your email address")
			)
