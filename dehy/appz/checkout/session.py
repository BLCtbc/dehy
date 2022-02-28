from oscar.apps.checkout import exceptions, session

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from dehy.appz.checkout import utils, tax
from bs4 import BeautifulSoup
from . import FORM_STRUCTURES
from oscar.core.loading import get_class, get_model

CheckoutSessionData = utils.CheckoutSessionData

class CheckoutSessionMixin(session.CheckoutSessionMixin):

	def dispatch(self, request, *args, **kwargs):
		# Assign the checkout session manager so it's available in all checkout
		# views.
		self.checkout_session = CheckoutSessionData(request)

		# Check if this view should be skipped
		try:
			self.check_skip_conditions(request)
		except exceptions.PassedSkipCondition as e:
			return http.HttpResponseRedirect(e.url)

		# Enforce any pre-conditions for the view.
		try:
			self.check_pre_conditions(request)
		except exceptions.FailedPreCondition as e:
			for message in e.messages:
				messages.warning(request, message)
			return http.HttpResponseRedirect(e.url)

		return super().dispatch(
			request, *args, **kwargs)

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

	def get_form_structure(self, form, use_placeholders=False, use_labels=False, use_help_text=False, label_exceptions=[]):
		outter_tags = ['select', 'input', 'fieldset']
		inner_tags = ['input', 'option']
		if use_labels or label_exceptions:
			outter_tags+=['label']
			inner_tags+=['label']

		if use_help_text:
			outter_tags+=[('span', 'helptext')]
			inner_tags+=[('span', 'helptext')]

		form_structure = [{'tag':'div', 'classes':'form-container', 'elems': []}]
		soup = BeautifulSoup(form().as_table(), 'html.parser')

		for elem in soup.find_all(outter_tags):
			elem_dict = {'tag': elem.name, 'attrs': elem.attrs}
			if elem.name == 'label':
				for_attr = elem.attrs['for']
				if not label_exceptions or for_attr not in label_exceptions:
					continue

				else:
					elem_dict['text'] = elem.text


			if elem.has_attr('required'):
				elem_dict['classes'] = 'required'

			if use_help_text and elem.name=='span' and 'helptext' in elem['class']:
				elem_dict.update({'text':elem.text})

			child_elems = []

			for child in elem.findChildren(inner_tags):
				child_elems.append({'tag':child.name, 'text': child.text, 'attrs':child.attrs})
				if child.has_attr('required'):
					child_elems[-1]['classes'] = 'required'

			if child_elems:
				elem_dict['elems'] = child_elems

			form_structure[-1]['elems'].append(elem_dict)

		form_structure.append(FORM_STRUCTURES.submit_button_error_container)
		return form_structure

