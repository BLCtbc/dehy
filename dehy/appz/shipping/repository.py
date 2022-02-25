from oscar.apps.shipping import repository
from dehy.appz.shipping import methods as _shipping_methods
# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods

# class Repository(repository.Repository):
# 	methods = (shipping_methods.Standard(), shipping_methods.Express())

class Repository(repository.Repository):

	def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):

		methods = [_shipping_methods.Standard()]
		if shipping_addr and shipping_addr.country.code == 'US':
			# Express is only available in the US

			#############################################################################
			## will need to implement some sort of API here to properly configure which
			## shipping methods are available to a user based on their geo location
			#############################################################################
			methods += [_shipping_methods.TwoDayExpress(), _shipping_methods.NextDayExpress()]
		else:
			methods += [_shipping_methods.TwoDayExpress(), _shipping_methods.NextDayExpress()]

		return methods