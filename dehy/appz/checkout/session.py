from oscar.apps.checkout import session
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from oscar.apps.checkout import exceptions
from dehy.appz.checkout import tax

class CheckoutSessionMixin(session.CheckoutSessionMixin):
	def check_user_email_is_captured(self, request):
		if not request.user.is_authenticated \
				and not self.checkout_session.get_guest_email():
			raise exceptions.FailedPreCondition(
				url=reverse('checkout:checkout'),
				message=_(
					"Please either sign in or enter your email address")
			)

	def build_submission(self, **kwargs):
		submission = super().build_submission(
			**kwargs)

		if submission['shipping_address'] and submission['shipping_method']:
			tax.apply_to(submission)

			# Recalculate order total to ensure we have a tax-inclusive total
			submission['order_total'] = self.get_order_totals(
				submission['basket'],
				submission['shipping_charge'])

		return submission