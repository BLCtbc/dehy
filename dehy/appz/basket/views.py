from oscar.apps.basket.views import BasketAddView as CoreBasketAddView
from oscar.apps.basket.views import BasketView as CoreBasketView

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
BasketLineFormSet, SavedLineFormSet = get_classes('basket.formsets', ('BasketLineFormSet', 'SavedLineFormSet'))

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

		quantity = request.POST.get('quantity', None)
		data = {}

		self.product = shortcuts.get_object_or_404(self.product_model, pk=kwargs['pk'])
		response = super().post(request, *args, **kwargs)

		data['basket_items'] = request.basket.num_items
		data['product'] = {'pk': self.product.pk, 'title':self.product.title}

		response = JsonResponse(data)
		return response

	def get_form_kwargs(self):
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

class BasketView(CoreBasketView):
	model = get_model('basket', 'Line')
	basket_model = get_model('basket', 'Basket')
	formset_class = BasketLineFormSet
	form_class = BasketLineForm
	factory_kwargs = {
		'extra': 0,
		'can_delete': True
	}
	template_name = 'dehy/basket/basket.html'

	def get_basket_voucher_form(self):
		"""
		This is a separate method so that it's easy to e.g. not return a form
		if there are no vouchers available.
		"""
		if self.request.resolver_match.url_name != 'checkout':
			return None
		return BasketVoucherForm()


	def post(self, request, *args, **kwargs):
		data = {}
		response = super().post(request, *args, **kwargs)

		# print('\n dir(self): ', dir(self))

		## object list tells you which products in the basket had their quantities updated
		print('\n object_list: ', self.object_list)

		# formset = self.get_formset()

		num_items = request.basket.num_items
		print('dir(request.basket):\n ', dir(request.basket))
		data['object_list'] = {}
		print('request.basket.is_tax_known:\n ', request.basket.is_tax_known)
		print('self.checkout_session.is_shipping_address_set():\n ', self.checkout_session.is_shipping_address_set())
		print('request.basket.strategy:\n ', request.basket.strategy)
		print('request.basket.strategy.pricing_policy:\n ', request.basket.strategy.pricing_policy)

		print('dir(request.basket.strategy):\n ', dir(request.basket.strategy))

		if request.basket.is_tax_known:
			print('request.basket.total_tax:\n ', request.basket.total_tax)
			data['total_tax'] = request.basket.total_tax

		for line in self.object_list:
			data['object_list'][line.product_id] = {'quantity': line.quantity, 'price': line.line_price_excl_tax}


		data['basket_num_items'] = request.basket.num_items
		data['order_total'] = request.basket.total_excl_tax_excl_discounts

		response = JsonResponse(data)
		return response
		# print(f'\n dir(response): {dir(response)}')
		#
		# print(f"\n request.POST: {request.POST}")
		# print(f'\ndir(self): {dir(self)}')
		# print(f'\ndir(request): {dir(request)}')
		#
		# print(f'\n kwargs: {kwargs}')
		#
		# kwargs = self.get_formset_kwargs()
		# print(f'\n kwargs: {kwargs}')
		#
		# strategy = kwargs.pop('strategy')
		# request.basket.strategy = strategy
		#
		# formset = self.formset_class(strategy, request.POST)
		# print('\n dir(formset): ', dir(formset))
		# # print('\n formset.total_form_count(): ', formset.total_form_count())
		#
		# print('\n dir(formset.forms): ', dir(formset.forms))
		#
		# print('\n formset_valid: ', self.formset_valid(formset))
		# response = self.formset_valid(formset)
		# print(f'\ndir(response): {dir(response)}')



