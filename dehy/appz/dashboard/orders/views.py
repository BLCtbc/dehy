from oscar.apps.dashboard.orders import views
from django.db.models import F, Q, Case, Max, When

class OrderListView(views.OrderListView):
	def get_queryset(self):
		queryset = super().get_queryset()
		if self.request.GET.get('sort'):
			trans_table = {'asc':'', 'desc':'-'}
			sort_order = trans_table[self.request.GET.get('dir')] if self.request.GET.get('dir') else ''
			sorting = sort_order+self.request.GET.get('sort')

			if 'email' in self.request.GET.get('sort'):
				queryset = queryset.annotate(email_address=Case(
						When(user__isnull=True, then=F('guest_email')),
						When(user__isnull=False, then=F('user__email')),
					)
				).order_by(sorting)

			else:
				queryset = queryset.order_by(sorting)

		return queryset

	def get_row_values(self, order):
		row = {'number': order.number, 'customer': order.email, 'num_items': order.num_items,
			   'date': order.date_placed, 'value': order.total_incl_tax,
			   'status': order.status}
		if order.shipping_address:
			row['shipping_address_name'] = order.shipping_address.name
		if order.billing_address:
			row['billing_address_name'] = order.billing_address.name
		return row