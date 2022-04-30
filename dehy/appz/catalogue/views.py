
from oscar.apps.catalogue import views
from dehy.appz.catalogue.models import Category, Product
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import InvalidPage
from oscar.core.loading import get_class
from django.utils.translation import gettext_lazy as _


get_product_search_handler_class = get_class('catalogue.search_handlers', 'get_product_search_handler_class')


# class CatalogueView(CoreCatalogueView):
# 	template_name = 'catalogue/browse.html'

class CatalogueView(views.CatalogueView):
	"""
	Browse all products in the catalogue
	"""
	context_object_name = "products"
	template_name = 'dehy/shop/browse.html'

	def get(self, request, *args, **kwargs):
		try:
			self.search_handler = self.get_search_handler(
				self.request.GET, request.get_full_path(), [])
		except InvalidPage:
			# Redirect to page one.
			messages.error(request, _('The given page number was invalid.'))
			return redirect('catalogue:index')
		return super().get(request, *args, **kwargs)

	def get_search_handler(self, *args, **kwargs):
		return get_product_search_handler_class()(*args, **kwargs)

	def get_context_data(self, **kwargs):


		context_data = super().get_context_data(**kwargs)
		context_data['summary'] = _("All products")
		search_context = self.search_handler.get_search_context_data(
			self.context_object_name)

		context_data.update(search_context)

		return context_data

class ProductCategoryView(views.ProductCategoryView):
	model = Category
	slug_field = 'slug'
	slug_url_kwarg = 'category_slug'
	template_name = 'dehy/shop/category.html'

	def get_context_data(self, *args, **kwargs):
		context_data = super().get_context_data(*args, **kwargs)
		return context_data

	def get_category(self):
		return get_object_or_404(Category, slug=self.kwargs['category_slug'])


class ProductDetailView(views.ProductDetailView):
	model = Product
	slug_field = 'slug'
	slug_url_kwarg = 'product_slug'
	template_name = 'dehy/shop/detail.html'

	# Whether to redirect to the URL with the right path
	enforce_paths = True

	# Whether to redirect child products to their parent's URL. If it's disabled,
	# we display variant product details on the separate page. Otherwise, details
	# displayed on parent product page.
	enforce_parent = False



