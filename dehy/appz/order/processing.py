from oscar.apps.order.processing import EventHandler as BaseEventHandler

class EventHandler(BaseEventHandler):
	def handle_shipping_event(self, order, event_type, lines, line_quantities, **kwargs):
		"""
		Handle a shipping event for a given order.
		This is most common entry point to this class - most of your order
		processing should be modelled around shipping events.  Shipping events
		can be used to trigger payment and communication events.
		You will generally want to override this method to implement the
		specifics of you order processing pipeline.
		"""
		print('\n handling shipping event \n')
		print('order: ', order.number)
		print('event_type: ', event_type)
		# Example implementation
		self.validate_shipping_event(order, event_type, lines, line_quantities, **kwargs)

		return self.create_shipping_event(order, event_type, lines, line_quantities, **kwargs)