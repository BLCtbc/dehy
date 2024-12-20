from django.apps import apps
from django.urls import include, path
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from dehy.appz.generic.sitemaps import StaticViewSitemap

sitemaps = {'static': StaticViewSitemap}

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('dehy.appz.generic.urls'), name='generic'),
	path('recipes/', include('dehy.appz.recipes.urls'), name='recipes'),
	path('wholesale/', include('dehy.appz.wholesale.urls'), name='wholesale'),
	path('', include(apps.get_app_config('dehy').urls[0])),
	path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

from django.conf import settings
if settings.DEBUG:
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns
	# urlpatterns += [
	# 	path('__debug__/', include('debug_toolbar.urls')),
	# ]
	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)