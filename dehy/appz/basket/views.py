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
		print(f"\n dir(request.basket): {dir(self.request.basket)}")

		"""
		This is a separate method so that it's easy to e.g. not return a form
		if there are no vouchers available.
		"""
		print(f'\n self.request.resolver_match: {self.request.resolver_match}')

		if self.request.resolver_match.url_name != 'checkout':
			return None

		return BasketVoucherForm()

	# def formset_valid(self, formset):
	# 	# Store offers before any changes are made so we can inform the user of
	# 	# any changes
	# 	offers_before = self.request.basket.applied_offers()
	# 	save_for_later = False
	#
	# 	# Keep a list of messages - we don't immediately call
	# 	# django.contrib.messages as we may be returning an AJAX response in
	# 	# which case we pass the messages back in a JSON payload.
	# 	flash_messages = ajax.FlashMessages()
	#
	# 	for form in formset:
	# 		print(f'\ndir(form.instance): {dir(form.instance)}')
	# 		if (hasattr(form, 'cleaned_data')
	# 				and form.cleaned_data.get('save_for_later', False)):
	# 			line = form.instance
	# 			if self.request.user.is_authenticated:
	# 				self.move_line_to_saved_basket(line)
	#
	# 				msg = render_to_string(
	# 					'oscar/basket/messages/line_saved.html',
	# 					{'line': line})
	# 				flash_messages.info(msg)
	#
	# 				save_for_later = True
	# 			else:
	# 				msg = _("You can't save an item for later if you're "
	# 						"not logged in!")
	# 				flash_messages.error(msg)
	# 				return redirect(self.get_success_url())
	#
	# 	if save_for_later:
	# 		# No need to call super if we're moving lines to the saved basket
	# 		response = redirect(self.get_success_url())
	# 	else:
	# 		# Save changes to basket as per normal
	# 		response = super().formset_valid(formset)
	#
	# 	# If AJAX submission, don't redirect but reload the basket content HTML
	# 	if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
	# 		# Reload basket and apply offers again
	# 		self.request.basket = get_model('basket', 'Basket').objects.get(
	# 			id=self.request.basket.id)
	# 		self.request.basket.strategy = self.request.strategy
	# 		Applicator().apply(self.request.basket, self.request.user,
	# 						   self.request)
	# 		offers_after = self.request.basket.applied_offers()
	#
	# 		for level, msg in BasketMessageGenerator().get_messages(
	# 				self.request.basket, offers_before, offers_after, include_buttons=False):
	# 			flash_messages.add_message(level, msg)
	#
	# 		# Reload formset - we have to remove the POST fields from the
	# 		# kwargs as, if they are left in, the formset won't construct
	# 		# correctly as there will be a state mismatch between the
	# 		# management form and the database.
	# 		kwargs = self.get_formset_kwargs()
	# 		del kwargs['data']
	# 		del kwargs['files']
	# 		if 'queryset' in kwargs:
	# 			del kwargs['queryset']
	# 		formset = self.get_formset()(queryset=self.get_queryset(),
	# 									 **kwargs)
	# 		ctx = self.get_context_data(formset=formset,
	# 									basket=self.request.basket)
	# 		return self.json_response(ctx, flash_messages)
	#
	# 	BasketMessageGenerator().apply_messages(self.request, offers_before)
	#
	# 	return response

	def post(self, request, *args, **kwargs):
		print('request.POST: ', request.POST)
		data = {}
		response = super().post(request, *args, **kwargs)

		# print('\n dir(self): ', dir(self))

		## object list tells you which products in the basket had their quantities updated
		print('\n object_list: ', self.object_list)

		# formset = self.get_formset()

		num_items = request.basket.num_items

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



