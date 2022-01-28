from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import CatalogueView as CoreCatalogueView

from dehy.appz.catalogue.models import Category, Product
from django.shortcuts import get_object_or_404, redirect

class CatalogueView(CoreCatalogueView):
	template_name = 'catalogue/browse.html'
	
class ProductCategoryView(CoreProductCategoryView):
	model = Category
	slug_field = 'slug'
	slug_url_kwarg = 'category_slug'
	template_name = 'catalogue/category.html'

	def get_category(self):
		return get_object_or_404(Category, slug=self.kwargs['category_slug'])

class ProductDetailView(CoreProductDetailView):
	model = Product
	template_name = 'catalogue/partials/product.html'
	# template_folder = "dehy/templates/catalogue"
	slug_field = 'slug'
	slug_url_kwarg = 'product_slug'

	def get(self, request, **kwargs):
		"""
		Ensures that the correct URL is used before rendering a response
		"""

		self.object = product = self.get_object() # gets the Product item
		redirect = self.redirect_if_necessary(request.path, product)
		if redirect is not None:
			return redirect

		# Do allow staff members so they can test layout etc.
		if not self.is_viewable(product, request):
			raise Http404()

		response = super().get(request, **kwargs)
		self.send_signal(request, response, product)
		return response