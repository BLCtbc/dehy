from oscar import config
from django.urls import path

class ShopConfig(config.Shop):
	name = 'dehy'
	namespace = 'shop'

	# Override get_urls method
	def get_urls(self):
		urls_to_remove = []
		urlpatterns = super().get_urls()
		for pattern in urlpatterns:
			if hasattr(pattern, 'name'):
				name = getattr(pattern, 'name', None)
				if name == 'home':
					urls_to_remove.append(pattern)


			if hasattr(pattern, 'namespace'):
				namespace = getattr(pattern, 'namespace', None)
				if namespace == 'catalogue':
					urls_to_remove.append(pattern)


		for pattern in urls_to_remove:
			urlpatterns.remove(pattern)


		urlpatterns += [
			path('shop/', self.catalogue_app.urls, name='shop'),
			# path('shop/', self.extra_view.as_view(), name='extra'),
			# all the remaining URLs, removed for simplicity
			# ...
		]

		return urlpatterns

