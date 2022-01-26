import oscar.apps.catalogue.apps as apps
from django.urls import include, path

class CatalogueConfig(apps.CatalogueConfig):
	name = 'dehy.appz.catalogue'

	def get_urls(self):
		urls = super().get_urls()
		disabled_url_names = ['detail', 'category']
		for urlpattern in urls[:]:
			if hasattr(urlpattern, 'name') and (urlpattern.name in disabled_url_names):
				urls.remove(urlpattern)

		urls += [
			path('p/<slug:product_slug>', self.detail_view.as_view(), name='detail'),
			path('<slug:category_slug>', self.category_view.as_view(), name='category'),
		]

		return self.post_process_urls(urls)

