from functools import wraps
import requests
from oscar.core.loading import get_class
from dehy.appz.catalogue.models import Product

class persist_basket_contents(object):
	# FROM: https://stackoverflow.com/a/41849076/6158303
	"""
	Some views, such as login and logout, will reset all session state.
	(via a call to ``request.session.cycle_key()`` or ``session.flush()``).
	That is a security measure to mitigate session fixation vulnerabilities.

	By applying this decorator, some values are retained.
	Be very aware what kind of variables you want to persist.
	"""

	def __init__(self, vars=None):
		self.vars = vars

	def __call__(self, view_func):

		@wraps(view_func)
		def inner(request, *args, **kwargs):
			# Backup first
			session_backup = {'basket_content': {}, 'basket_id': ''}
			# _response = session.get(request.get_raw_uri())
			basket = request.basket

			try:
				for line in request.basket.all_lines():
					session_backup['basket_content'][line.product.id] = line.quantity

			except KeyError:
				pass


			# Call the original view
			response = view_func(request, *args, **kwargs)

			if not request.basket.is_empty:

				request.session.update({'basket_content': session_backup['basket_content'], 'basket_id': request.basket.id})
				# request.basket.merge(basket, False)
				request.basket.flush()

			basket_content = request.session.get('basket_content', None)

			print('\n request.session.items: ', request.session.items())
			print('\n *** basket status: ', request.basket.status)

			if basket_content:
				for key, val in basket_content.items():
					product = Product._default_manager.filter(id=key)
					if product:
						product = product.first()
						request.basket.add_product(product, val)

				request.basket.save()


			request.session.modified = True
			print('decorator3: ', request.basket)

			return response

		return inner
