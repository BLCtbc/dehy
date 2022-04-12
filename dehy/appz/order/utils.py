# from oscar.apps.order.utils import OrderCreator as CoreOrderCreator
#
# class OrderCreator(CoreOrderCreator):
#     """
#     Places the order by writing out the various models
#     """
# 	def place_order(self, basket, total,  # noqa (too complex (12))
#         shipping_method, shipping_charge, user=None, shipping_address=None, billing_address=None,
#         order_number=None, status=None, request=None, surcharges=None,
# 		additional_info_questionnaire=None, **kwargs):
#         """
#         Placing an order involves creating all the relevant models based on the
#         basket and session data.
#         """
#         if basket.is_empty:
#             raise ValueError(_("Empty baskets cannot be submitted"))
#         if not order_number:
#             generator = OrderNumberGenerator()
#             order_number = generator.order_number(basket)
#         if not status and hasattr(settings, 'OSCAR_INITIAL_ORDER_STATUS'):
#             status = getattr(settings, 'OSCAR_INITIAL_ORDER_STATUS')
#
#         if Order._default_manager.filter(number=order_number).exists():
#             raise ValueError(_("There is already an order with number %s")
#                              % order_number)
#
#         with transaction.atomic():
#
#             kwargs['surcharges'] = surcharges
#             # Ok - everything seems to be in order, let's place the order
#             order = self.create_order_model(
#                 user, basket, shipping_address, shipping_method, shipping_charge,
#                 billing_address, total, order_number, status, request, additional_info_questionnaire, **kwargs)
#             for line in basket.all_lines():
#                 self.create_line_models(order, line)
#                 self.update_stock_records(line)
#
#             for voucher in basket.vouchers.select_for_update():
#                 if not voucher.is_active():  # basket ignores inactive vouchers
#                     basket.vouchers.remove(voucher)
#                 else:
#                     available_to_user, msg = voucher.is_available_to_user(user=user)
#                     if not available_to_user:
#                         raise ValueError(msg)
#
#             # Record any discounts associated with this order
#             for application in basket.offer_applications:
#                 # Trigger any deferred benefits from offers and capture the
#                 # resulting message
#                 application['message'] \
#                     = application['offer'].apply_deferred_benefit(basket, order,
#                                                                   application)
#                 # Record offer application results
#                 if application['result'].affects_shipping:
#                     # Skip zero shipping discounts
#                     shipping_discount = shipping_method.discount(basket)
#                     if shipping_discount <= D('0.00'):
#                         continue
#                     # If a shipping offer, we need to grab the actual discount off
#                     # the shipping method instance, which should be wrapped in an
#                     # OfferDiscount instance.
#                     application['discount'] = shipping_discount
#                 self.create_discount_model(order, application)
#                 self.record_discount(application)
#
#             for voucher in basket.vouchers.all():
#                 self.record_voucher_usage(order, voucher, user)
#
#         # Send signal for analytics to pick up
#         order_placed.send(sender=self, order=order, user=user)
#
#         return order
#
#
# 		def create_order_model(self, user, basket, shipping_address,
#                shipping_method, shipping_charge, billing_address,
#                total, order_number, status, request=None, surcharges=None, **extra_order_fields):
#         """Create an order model."""
#         order_data = {'basket': basket,
#                       'number': order_number,
#                       'currency': total.currency,
#                       'total_incl_tax': total.incl_tax,
#                       'total_excl_tax': total.excl_tax,
#                       'shipping_incl_tax': shipping_charge.incl_tax,
#                       'shipping_excl_tax': shipping_charge.excl_tax,
#                       'shipping_method': shipping_method.name,
#                       'shipping_code': shipping_method.code}
#         if shipping_address:
#             order_data['shipping_address'] = shipping_address
#         if billing_address:
#             order_data['billing_address'] = billing_address
#         if user and user.is_authenticated:
#             order_data['user_id'] = user.id
#         if status:
#             order_data['status'] = status
#         if extra_order_fields:
#             order_data.update(extra_order_fields)
#         if 'site' not in order_data:
#             order_data['site'] = Site._default_manager.get_current(request)
#         order = Order(**order_data)
#         order.save()
#         if surcharges is not None:
#             for charge in surcharges:
#                 Surcharge.objects.create(
#                     order=order,
#                     name=charge.surcharge.name,
#                     code=charge.surcharge.code,
#                     excl_tax=charge.price.excl_tax,
#                     incl_tax=charge.price.incl_tax
#                 )
#         return order
