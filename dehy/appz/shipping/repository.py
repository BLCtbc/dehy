from oscar.apps.shipping import repository
from . import methods
# https://django-oscar.readthedocs.io/en/latest/howto/how_to_configure_shipping.html?highlight=shipping%20method#shipping-methods

class Repository(repository.Repository):
    methods = (methods.Standard(), methods.Express())