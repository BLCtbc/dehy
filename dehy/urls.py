
from django.apps import apps
from django.urls import include, path
from django.contrib import admin
from . import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('custom/', views.CustomView.as_view(), name='custom'),
	path('returns/', views.ReturnsRefundsView.as_view(), name='returns'),
	path('recipes/', views.RecipesView.as_view(), name='recipes'),
	path('wholesale/', views.WholesaleView.as_view(), name='wholesale'),
	path('contact/', views.ContactView.as_view(), name='contact'),
	path('', views.HomeView.as_view(), name='home'),
	path('', include(apps.get_app_config('dehy').urls[0])),
	path('ajax/get_cart_quantity/', views.get_cart_quantity, name='get_cart_quantity'),
]

from django.conf import settings
if settings.DEBUG:
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns
	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)