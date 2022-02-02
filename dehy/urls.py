from django.apps import apps
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('dehy.appz.generic.urls'), name='generic'),
	path('', include('dehy.appz.recipes.urls'), name='recipes'),
	path('', include(apps.get_app_config('dehy').urls[0])),
]

from django.conf import settings
if settings.DEBUG:
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns
	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)