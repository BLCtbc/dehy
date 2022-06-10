from oscar.apps.dashboard.orders import views

class OrderListView(views.OrderListView):
	def get_row_values(self, order):
		row = {'number': order.number, 'customer': order.email, 'num_items': order.num_items,
			   'date': order.date_placed, 'value': order.total_incl_tax,
			   'status': order.status}
		if order.shipping_address:
			row['shipping_address_name'] = order.shipping_address.name
		if order.billing_address:
			row['billing_address_name'] = order.billing_address.name
		return row