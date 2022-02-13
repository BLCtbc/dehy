from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import CatalogueView as BrowseView

from dehy.appz.catalogue.models import Category, Product
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import InvalidPage
from oscar.core.loading import get_class
from django.utils.translation import gettext_lazy as _

get_product_search_handler_class = get_class('catalogue.search_handlers', 'get_product_search_handler_class')


# class CatalogueView(CoreCatalogueView):
# 	template_name = 'catalogue/browse.html'

class CatalogueView(BrowseView):
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
		ctx = {}
		ctx['summary'] = _("All products")
		search_context = self.search_handler.get_search_context_data(
			self.context_object_name)

		ctx.update(search_context)

		return ctx

class ProductCategoryView(CoreProductCategoryView):
	model = Category
	slug_field = 'slug'
	slug_url_kwarg = 'category_slug'
	template_name = 'dehy/shop/category.html'


	def get_category(self):
		return get_object_or_404(Category, slug=self.kwargs['category_slug'])


class ProductDetailView(CoreProductDetailView):
	model = Product
	slug_field = 'slug'
	slug_url_kwarg = 'product_slug'
	template_name = 'dehy/shop/detail.html'


