default_app_config = 'dehy.appz.checkout.apps.CheckoutConfig'
PAYMENT_EVENT_PURCHASE = 'Purchase'
PAYMENT_METHOD_STRIPE = 'Stripe'
STRIPE_EMAIL = 'stripeEmail'
STRIPE_TOKEN = 'stripeToken'

class FormStructure(object):

	def get_submit_button(self, button_text):

		submit_button_container = {
			'tag':'div',
			'classes':'form-group row',
			'elems': [
				{
					'tag':'button',
					'text': button_text,
					'classes': 'col-12',
					'attrs': {
						'type': 'submit', 'hidden': '', 'aria-label':button_text
					}
				}
			],
		}
		return submit_button_container

	def get_errors_container(self):
		error_container = {
			'tag':'div',
			'classes':'form-group row hide',
			'attrs': {'id': 'error_container'},
			'elems': [
				{
					'tag':'div',
					'classes': 'col-12 errors',
					'attrs': {
						'id': 'errors',
					}
				}]
		}
		return error_container


	def get_submit_button_error_container(self, submit_text='Continue'):
		submit_button_error_container = {
			'tag': 'div',
			'classes': 'error-container button-container',
			'elems': [self.get_errors_container(), self.get_submit_button(submit_text)],
		}
		return submit_button_error_container


