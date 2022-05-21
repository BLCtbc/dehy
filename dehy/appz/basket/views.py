from oscar.apps.basket.views import BasketView as CoreBasketView
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core import ajax
from oscar.apps.basket.signals import basket_addition
from oscar.core.loading import get_class, get_classes, get_model
from sorl.thumbnail import get_thumbnail

from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse, QueryDict
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, View
from django import shortcuts
from django.shortcuts import redirect

from sorl.thumbnail import get_thumbnail


from decimal import Decimal as D
TWO_PLACES = D(10)**-2

from dehy.appz.checkout.facade import facade

from dehy.appz.checkout import views as checkout_views

import json
from oscar.core.utils import redirect_to_referrer, safe_referrer


(BasketLineForm, AddToBasketForm, BasketVoucherForm, SavedLineForm) = get_classes('basket.forms', ('BasketLineForm', 'AddToBasketForm','BasketVoucherForm', 'SavedLineForm'))
BasketLineFormSet, SavedLineFormSet = get_classes('basket.formsets', ('BasketLineFormSet', 'SavedLineFormSet'))
ShippingView = get_class('checkout.views', 'ShippingView')
BasketMessageGenerator = get_class('basket.utils', 'BasketMessageGenerator')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
Repository = get_class('shipping.repository', 'Repository')
CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')

UserAddress = get_model('address', 'UserAddress')
ShippingAddress = get_model('order', 'ShippingAddress')
Country = get_model('address', 'Country')
Repository = get_class('shipping.repository', 'Repository')
Applicator = get_class('offer.applicator', 'Applicator')
# Product = get_model('catalogue', 'Product')

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
		data = {'object_list': {}}

		self.product = shortcuts.get_object_or_404(self.product_model, pk=kwargs['pk'])


		data['object_list'][self.product.id] = {
			'quantity': quantity,
			'url': self.product.get_absolute_url(),
			'price': self.product.stockrecords.first().price * D(quantity),
			'id': self.product.id,
		}


		img = self.product.primary_image()

		if img:
			img = img.original
			thumbnail = get_thumbnail(img, '200', crop='center', quality=99)
			data['object_list'][self.product.id].update({'img_url':thumbnail.url})

		response = super().post(request, *args, **kwargs)

		data['basket_num_items'] = request.basket.num_items
		title =  self.product.title

		if self.product.is_child:
			data['object_list'][self.product.id].update({'size': title})
			title = self.product.parent.title

		data['object_list'][self.product.id].update({'title': title})

		data['subtotal'] = D(request.basket.total_excl_tax_excl_discounts).quantize(TWO_PLACES)

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

	def get_shipping_address(self, basket):

		addr_data = self.checkout_session.new_shipping_address_fields()
		if addr_data:
			# Load address data into a blank shipping address model
			return ShippingAddress(**addr_data)

		addr_id = self.checkout_session.shipping_user_address_id()
		if addr_id:
			try:
				address = UserAddress._default_manager.get(pk=addr_id)
			except UserAddress.DoesNotExist:
				return None
			else:
				# Copy user address data into a blank shipping address instance
				shipping_addr = ShippingAddress()
				address.populate_alternative_model(shipping_addr)
				return shipping_addr

	def get_shipping_methods(self, basket):
		pass
		# if 'checkout' in self.request.resolver_match.app_names:
		# 	return Repository().get_shipping_methods(
		# 		basket=self.request.basket, user=self.request.user,
		# 		request=self.request)

	def get_default_shipping_method(self, basket):
		# if 'checkout' in self.request.resolver_match.app_names:
		# 	return Repository().get_default_shipping_method(
		# 		basket=self.request.basket, user=self.request.user,
		# 		request=self.request, shipping_addr=self.get_default_shipping_address())
		#
		# else:

		return Repository().get_free_shipping()


	def dispatch(self, request, *args, **kwargs):
		# We add an instance of checkout session data so its available in the basket view.
		# This is useful since we

		self.checkout_session = CheckoutSessionData(request)
		return super().dispatch(request, *args, **kwargs)

	def get_basket_voucher_form(self):
		"""
		This is a separate method so that it's easy to e.g. not return a form
		if there are no vouchers available.
		"""
		if self.request.resolver_match.url_name != 'checkout':
			return None
		return BasketVoucherForm()

	def post(self, request, *args, **kwargs):
		data = {'object_list': {}}
		response = super().post(request, *args, **kwargs)

		for line in self.object_list:
			data['object_list'][line.product_id] = {'quantity': line.quantity, 'price': line.line_price_excl_tax}

		num_items = request.basket.num_items

		data['basket_num_items'] = request.basket.num_items
		data['subtotal'] = D(request.basket.total_excl_tax_excl_discounts).quantize(TWO_PLACES)

		data['total_tax'] = D(0.00).quantize(TWO_PLACES)
		data['order_total'] = data['subtotal']

		if 'checkout' in self.request.resolver_match.app_names and self.checkout_session.is_shipping_address_set() and self.checkout_session.is_shipping_method_set(request.basket):
			shipping_addr = request.POST.get('shipping_addr', None)

			shipping_addr = json.loads(shipping_addr) if shipping_addr else self.get_shipping_address(request.basket)

			fields = ['first_name', 'last_name', 'line1', 'line2', 'line4', 'postcode', 'state', 'country', 'phone_number']
			shipping_fields = dict(zip(fields, shipping_addr.get_field_values(fields)))

			if len(shipping_fields['country']) > 2:
				ctry = Country.objects.get(printable_name=shipping_fields['country'])
				shipping_fields['country'] = ctry.iso_3166_1_a2

			data['shipping_methods'] = checkout_views.get_shipping_methods(request, shipping_fields, True)
			data['method_code'] = self.checkout_session.shipping_method_code(request.basket)

			shipping_method = next(filter(lambda x: x['code'] == data['method_code'], data['shipping_methods']), None)

			if shipping_method:
				data['shipping_charge'] = shipping_method['cost']
				if 'Referer' in self.request.headers.keys() and 'checkout' in self.request.headers['Referer']:
					order = facade.update_or_create_order(request.basket, shipping_fields=shipping_fields, shipping_method=shipping_method)
					data['total_tax'] = D(order.total_details.amount_tax/100).quantize(TWO_PLACES)

					request.basket._total_tax = data['total_tax']
					request.basket.save()
					data['order_total'] += (D(data['shipping_charge']).quantize(TWO_PLACES) + data['total_tax'])
					# data['order_total'] = str(data['order_total'])

		# remove empty dict
		if 'shipping_methods' in data.keys() and not data['shipping_methods']:
			data.pop('shipping_methods')

		response = JsonResponse(data)
		return response


	def formset_valid(self, formset):
		# Store offers before any changes are made so we can inform the user of
		# any changes
		offers_before = self.request.basket.applied_offers()
		save_for_later = False

		# Keep a list of messages - we don't immediately call
		# django.contrib.messages as we may be returning an AJAX response in
		# which case we pass the messages back in a JSON payload.
		flash_messages = ajax.FlashMessages()

		for form in formset:
			if (hasattr(form, 'cleaned_data')
					and form.cleaned_data.get('save_for_later', False)):
				line = form.instance
				if self.request.user.is_authenticated:
					self.move_line_to_saved_basket(line)

					msg = render_to_string(
						'oscar/basket/messages/line_saved.html',
						{'line': line})
					flash_messages.info(msg)

					save_for_later = True
				else:
					msg = _("You can't save an item for later if you're "
							"not logged in!")
					flash_messages.error(msg)
					return redirect(self.get_success_url())

		if save_for_later:
			# No need to call super if we're moving lines to the saved basket
			response = redirect(self.get_success_url())
		else:
			# Save changes to basket as per normal
			response = super().formset_valid(formset)

		# If AJAX submission, don't redirect but reload the basket content HTML
		if self.request.is_ajax:
			# Reload basket and apply offers again
			self.request.basket = get_model('basket', 'Basket').objects.get(
				id=self.request.basket.id)
			self.request.basket.strategy = self.request.strategy
			Applicator().apply(self.request.basket, self.request.user,
							   self.request)
			offers_after = self.request.basket.applied_offers()

			for level, msg in BasketMessageGenerator().get_messages(
					self.request.basket, offers_before, offers_after, include_buttons=False):
				flash_messages.add_message(level, msg)

			# Reload formset - we have to remove the POST fields from the
			# kwargs as, if they are left in, the formset won't construct
			# correctly as there will be a state mismatch between the
			# management form and the database.
			kwargs = self.get_formset_kwargs()
			del kwargs['data']
			del kwargs['files']
			if 'queryset' in kwargs:
				del kwargs['queryset']
			formset = self.get_formset()(queryset=self.get_queryset(),
										 **kwargs)
			ctx = self.get_context_data(formset=formset,
										basket=self.request.basket)
			return self.json_response(ctx, flash_messages)

		BasketMessageGenerator().apply_messages(self.request, offers_before)

		return response
