from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse, QueryDict
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, View
from oscar.core.loading import get_class, get_classes, get_model
from django import shortcuts
from django.shortcuts import redirect
from oscar.apps.basket.signals import (basket_addition, voucher_addition, voucher_removal)
from oscar.core import ajax
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import redirect_to_referrer, safe_referrer

(BasketLineForm, AddToBasketForm, BasketVoucherForm, SavedLineForm) = get_classes('basket.forms', ('BasketLineForm', 'AddToBasketForm','BasketVoucherForm', 'SavedLineForm'))

BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')

class BasketAddView(FormView):
	"""
	Handles the add-to-basket submissions, which are triggered from various
	parts of the site. The add-to-basket form is loaded into templates using
	a templatetag from :py:mod:`oscar.templatetags.basket_tags`.
	"""
	form_class = AddToBasketForm
	product_model = get_model('catalogue', 'product')
	add_signal = basket_addition
	http_method_names = ['post']

	def post(self, request, *args, **kwargs):
		print('*** post()')

		quantity = request.POST.get('quantity', None)
		data = {}

		self.product = shortcuts.get_object_or_404(self.product_model, pk=kwargs['pk'])
		response = super().post(request, *args, **kwargs)


		# response = super().post(request, *args, **kwargs)
		# form = self.get_form(self.form_class)

		# print(f"\n form.is_valid(): {form.is_valid()}")

		# if request.is_ajax() and self.form_valid(form):
		# 	print(f'self.form_valid(form): {self.form_valid(form)}')
		# 	# data['product'] = {
		# 	# 	'name': form.product,
		# 	# 	'price': self.product.price,
		# 	# 	'quantity': form.cleaned_data['quantity']
		# 	# }
		#
		# 	status_code = 200
		# 	response = JsonResponse(data)
		# else:
		# 	pass
		print(f'\n dir(request.basket): {dir(request.basket)}')
		print(f'\n request.basket.num_items: {request.basket.num_items}')
		print(f'\n request.basket.num_lines: {request.basket.num_lines}')

		data['basket_items'] = request.basket.num_items
		data['product'] = {'pk': self.product.pk, 'title':self.product.title}
		
		response = JsonResponse(data)
		return response

	def get_form_kwargs(self):
		print('get_form_kwargs')
		kwargs = super().get_form_kwargs()
		kwargs['basket'] = self.request.basket
		kwargs['product'] = self.product
		return kwargs

	def form_invalid(self, form):

		msgs = []
		for error in form.errors.values():
			msgs.append(error.as_text())
		clean_msgs = [m.replace('* ', '') for m in msgs if m.startswith('* ')]
		messages.error(self.request, ",".join(clean_msgs))

		return redirect_to_referrer(self.request, 'basket:summary')

	def form_valid(self, form):
		print('form_valid()')

		offers_before = self.request.basket.applied_offers()

		self.request.basket.add_product(
			form.product, form.cleaned_data['quantity'],
			form.cleaned_options())

		messages.success(self.request, self.get_success_message(form),
						 extra_tags='safe noicon')

		# Check for additional offer messages
		BasketMessageGenerator().apply_messages(self.request, offers_before)

		# Send signal for basket addition
		self.add_signal.send(
			sender=self, product=form.product, user=self.request.user,
			request=self.request)

		return super().form_valid(form)


	def get_success_url(self):
		post_url = self.request.POST.get('next')
		if post_url and url_has_allowed_host_and_scheme(post_url, self.request.get_host()):
			return post_url
		return safe_referrer(self.request, 'basket:summary')


	def get_success_message(self, form):
		return render_to_string(
			'oscar/basket/messages/addition.html',
			{'product': form.product,
			 'quantity': form.cleaned_data['quantity']})
